#!/usr/bin/env python

from pathlib import Path

import fire
import pysrt

from .log import logger


class SubtitleFixer:
    """Utility for fixing subtitles.

    Attributes:
        dir (str, optional): Default path to work on
    """

    BACKUP_EXT = ".bkp"
    MOVIE_EXTS = ["*.mkv", "*.avi", "*.mp4"]
    SUB_EXTS = ["*.srt", "*.sub"]
    SUB_BKP_EXTS = [f"{ext}{BACKUP_EXT}" for ext in SUB_EXTS]

    def __init__(self, dir="."):
        super().__init__()
        self.dir = Path(dir)

    def movies(self, dir=None):
        """Get movie paths.

        Args:
            dir (str, optional): Folder where to search for movies

        Returns:
            list: List of movie paths
        """

        dir = Path(dir or self.dir)
        return sum(
            (
                sorted(dir.glob(ext), key=lambda p: str(p).lower())
                for ext in self.MOVIE_EXTS
            ),
            [],
        )

    def subtitles(self, dir=None):
        """Get subtitle paths.

        Args:
            dir (str, optional): Folder where to search for subtitles

        Returns:
            list: List of subtitle paths
        """

        dir = Path(dir or self.dir)
        return sum(
            (
                sorted(dir.glob(ext), key=lambda p: str(p).lower())
                for ext in self.SUB_EXTS
            ),
            [],
        )

    def subtitle_backups(self, dir=None):
        """Get subtitle backup paths.

        Args:
            dir (str, optional): Folder where to search for backups

        Returns:
            list: List of subtitle backup paths
        """

        dir = Path(dir or self.dir)
        return sum(
            (
                sorted(dir.glob(ext), key=lambda p: str(p).lower())
                for ext in self.SUB_BKP_EXTS
            ),
            [],
        )

    def recode(
        self,
        dir=None,
        subtitle=None,
        source="windows-1250",
        target="utf-8",
        start_index=0,
        stop_index=None,
        force=False,
    ):
        """Re-encode subtitle using a different encoding.

        Args:
            dir (str, optional): Folder where to apply the recode
            subtitle (str, optional): Subtitle to recode
            source (str, optional): Source encoding of subtitle
            target (str, optional): Target encoding of subtitle
            start_index (int, optional): First index of subtitle list
            stop_index (None, optional): Last index of subtitle list
        """

        dir = Path(dir or self.dir)
        if subtitle:
            subtitles = [Path(subtitle)]
        else:
            subtitles = self.subtitles(dir)
        for sub in subtitles[start_index:stop_index]:
            try:
                text = sub.read_text(encoding=source)
            except Exception:
                logger.error(f"{sub.name} is not encoded as {source}")
            else:
                self.backup(sub, force)
                sub.write_bytes(text.encode(target))
                logger.info(f"Re-encoded {sub.name} as {target}")

    def rename(self, dir=None, start_index=0, stop_index=None, force=False):
        """Rename subtitles with the same name as the movie files.

        Args:
            dir (str, optional): Folder where to apply the rename
            start_index (int, optional): First index of subtitle list
            stop_index (None, optional): Last index of subtitle list
        """

        dir = Path(dir or self.dir)
        for sub, movie in list(zip(self.subtitles(dir), self.movies(dir)))[
            start_index:stop_index
        ]:
            newsub = sub.with_name(movie.stem + sub.suffix)
            if sub != newsub:
                self.backup(sub, force)
                sub.replace(newsub)
                logger.info(f"Renamed {sub.name} to {newsub.name}")

    def restore(self, dir=None, subtitle=None, start_index=0, stop_index=None):
        """Restore subtitle backups.

        Args:
            dir (str, optional): Folder where to apply the restore
            subtitle (str, optional): Subtitle to restore
            start_index (int, optional): First index of subtitle list
            stop_index (None, optional): Last index of subtitle list
        """

        dir = Path(dir or self.dir)
        if subtitle:
            subtitles = [Path(subtitle)]
        else:
            subtitles = self.subtitle_backups(dir)
        for sub in subtitles[start_index:stop_index]:
            newsub = sub.with_suffix("")
            sub.replace(newsub)
            logger.info(f"Restored {sub.name} as {newsub.name}")

    def shift(
        self, dir=None, subtitle=None, start_index=0, stop_index=None, force=True, **by
    ):
        """Shift subtitles by a ratio or an offset.

        Args:
            dir (str, optional): Folder where to apply the fixes
            start_index (int, optional): First index of subtitle list
            stop_index (None, optional): Last index of subtitle list
            **by (dict): Pysrt `shift` arguments
        """

        if not subtitle:
            dir = Path(dir or self.dir)
            subtitles = self.subtitles(dir)[start_index:stop_index]
        else:
            subtitles = [subtitle]

        for subtitle in subtitles:
            self.backup(subtitle, force)
            sub = pysrt.open(subtitle)
            sub.shift(**by)
            sub.save(subtitle)
            logger.info(f"Shifted {subtitle} by {by.items()}")

    def backup(self, subtitle, force=False):
        bkp = subtitle.with_suffix(f"{subtitle.suffix}{self.BACKUP_EXT}")
        if bkp.exists() and not force:
            logger.warning("Skipping backup of %s as it already exists", subtitle)
            return
        bkp.write_bytes(subtitle.read_bytes())
        logger.info("Backed up %s as %s", subtitle, bkp)

    def fix(self, dir=None, start_index=0, stop_index=None):
        """Attempt to apply all possible fixes:
                * rename
                * recode

        Args:
            dir (str, optional): Folder where to apply the fixes
            start_index (int, optional): First index of subtitle list
            stop_index (None, optional): Last index of subtitle list
        """

        dir = Path(dir or self.dir)
        self.recode(dir, start_index=start_index, stop_index=stop_index)
        self.rename(dir, start_index=start_index, stop_index=stop_index)


def main():
    """Main function."""

    fire.Fire(SubtitleFixer)


if __name__ == "__main__":
    main()
