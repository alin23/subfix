#!/usr/bin/env python

from pathlib import Path

import fire
import pysrt
import daiquiri

daiquiri.setup(outputs=(
    daiquiri.output.STDERR,
    daiquiri.output.File(directory="/tmp"),
))
logger = daiquiri.getLogger()


class SubtitleFixer():
    MOVIE_EXTS = ['*.mkv', '*.avi', '*.mp4']
    SUB_EXTS = ['*.srt', '*.sub']

    def __init__(self, dir='.'):
        super().__init__()
        self.dir = Path(dir)

    def movies(self, dir=None):
        dir = Path(dir or self.dir)
        return sum((sorted(dir.glob(ext), key=lambda p: str(p).lower()) for ext in self.MOVIE_EXTS), [])

    def subtitles(self, dir=None):
        dir = Path(dir or self.dir)
        return sum((sorted(dir.glob(ext), key=lambda p: str(p).lower()) for ext in self.SUB_EXTS), [])

    def recode(self, dir=None, subtitle=None, source='windows-1250', target='utf-8', start_index=0, stop_index=None):
        dir = Path(dir or self.dir)
        if subtitle:
            subtitles = [Path(subtitle)]
        else:
            subtitles = self.subtitles(dir)
        for sub in subtitles[start_index:stop_index]:
            try:
                text = sub.read_text(encoding=source)
            except Exception:
                logger.error(f'{sub.name} is not encoded as {source}')
            else:
                sub.write_bytes(text.encode(target))
                logger.info(f'Re-encoded {sub.name} as {target}')

    def rename(self, dir=None, start_index=0, stop_index=None):
        dir = Path(dir or self.dir)
        for sub, movie in list(zip(self.subtitles(dir), self.movies(dir)))[start_index:stop_index]:
            newsub = sub.with_name(movie.stem + sub.suffix)
            if sub != newsub:
                sub.replace(newsub)
                logger.info(f'Renamed {sub.name} to {newsub.name}')

    def shift(self, dir=None, start_index=0, stop_index=None, **by):
        dir = Path(dir or self.dir)
        for subtitle in self.subtitles(dir)[start_index:stop_index]:
            sub = pysrt.open(subtitle)
            sub.shift(**by)
            sub.save(subtitle)
            logger.info(f'Shifted {subtitle} by {by.items()}')

    def fix(self, dir=None, start_index=0, stop_index=None):
        dir = Path(dir or self.dir)
        self.recode(dir, start_index=start_index, stop_index=stop_index)
        self.rename(dir, start_index=start_index, stop_index=stop_index)


def main():
    fire.Fire(SubtitleFixer)


if __name__ == '__main__':
    main()
