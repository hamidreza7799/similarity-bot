import logging
import os
import random
import re


# from scipy.special import softmax


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PathUtil:
    @staticmethod
    def unify_path(path):
        return path.replace('\\', '/')

    @staticmethod
    def path_to_name(path, remove_ext=False):
        path = PathUtil.unify_path(path)
        name_start = path.rfind('/') + 1  # / not fount: -1 + 1 = 0
        full_name = path[name_start:]
        if remove_ext:
            last_dot = full_name.rfind('.')
            return full_name[:last_dot]
        return path[name_start:]

    @staticmethod
    def path_to_ext(path):
        last_dot = path.rfind('.')
        return path[last_dot + 1:]

    @staticmethod
    def path_to_dir(path):
        path = PathUtil.unify_path(path)
        name_start = path.rfind('/') + 1  # / not fount: -1 + 1 = 0
        full_dir = path[:name_start] or '.'
        return full_dir

    @staticmethod
    def path_dir_mux(full_path, directory, target_ext, alt_path):

        if full_path:
            if target_ext is not None and PathUtil.path_to_ext(full_path) != target_ext:
                logging.warning(f' {full_path} is not matching target extension: {target_ext}')
            return full_path
        elif directory and target_ext:
            return f'{directory}/{PathUtil.path_to_name(alt_path, remove_ext=True)}.{target_ext}'
        elif target_ext:
            return f'{PathUtil.path_to_dir(alt_path)}/{PathUtil.path_to_name(alt_path, remove_ext=True)}.{target_ext}'
        else:
            raise Exception('Invalid Path/Dir/Ext Arguments!')

    @staticmethod
    def files_in_dir(full_dir, target_ext=None, nested=False, shuffle=False):

        target_exts = [target_ext] if isinstance(target_ext, str) else target_ext
        files = []

        for root, dirs, names in os.walk(full_dir):
            for name in names:
                if not target_ext or PathUtil.path_to_ext(name) in target_exts:
                    files.append(PathUtil.unify_path(os.path.join(root, name)))

            if not nested:
                break

        if shuffle:
            random.shuffle(files)
        return files


class TimeUtil:
    @staticmethod
    def split_time(milis, hours=False):
        seconds = milis // 1000
        minutes = seconds // 60
        seconds = seconds % 60

        if hours:
            hours = minutes // 60
            minutes = minutes % 60
            return hours, minutes, seconds, int(milis % 1000)
        else:
            return minutes, seconds, int(milis % 1000)

    @staticmethod
    def format_timestamp(milis, hours=False):
        if hours:
            time_str = '%2d-%2d-%2d-%3d' % TimeUtil.split_time(milis, True)
        else:
            time_str = '%3d-%2d-%3d' % TimeUtil.split_time(milis, False)
        return time_str.replace(' ', '0')

    @staticmethod
    def format_time(milis, pattern='h-M-s'):
        hours, minutes, seconds, milis = TimeUtil.split_time(milis, True)
        minute_digits, second_digits = 2, 2
        if 'h' not in pattern:
            minutes += hours * 60
            minute_digits = 3
        if 'M' not in pattern:
            seconds += minutes * 60
            second_digits = 3
        formatted = pattern.replace('h', str(hours).rjust(2, '0'))
        formatted = formatted.replace('M', str(minutes).rjust(minute_digits, '0'))
        formatted = formatted.replace('s', str(seconds).rjust(second_digits, '0'))
        formatted = formatted.replace('m', str(milis).rjust(3, '0'))
        return formatted

    @staticmethod
    def format_duration(milis):
        time_str = '%3d-%3d' % (milis // 1000, int(milis % 1000))
        return time_str.replace(' ', '0')

    @staticmethod
    def parse_time(time_str, pattern='h-M-s', sep='-'):

        values = list(map(int, time_str.split(sep)))
        units = pattern.split(sep)

        milis = 0

        for value, unit in zip(values, units):
            if unit == 'h':
                milis += value * 1000 * 60 * 60
            elif unit == 'M':
                milis += value * 1000 * 60
            elif unit == 's':
                milis += value * 1000
            elif unit == 'm':
                milis += value
        return milis

    @staticmethod
    def parse_time_re(time_str, pattern='M:s.m-x', sep='[^0-9a-zA-Z]'):

        sep_re = re.compile(sep)
        units = sep_re.split(pattern)
        values = list(map(int, sep_re.split(time_str)))

        milis = 0

        for value, unit in zip(values, units):
            if unit == 'h':
                milis += value * 1000 * 60 * 60
            elif unit == 'M':
                milis += value * 1000 * 60
            elif unit == 's':
                milis += value * 1000
            elif unit == 'm':
                milis += value
        return milis

    @staticmethod
    def parse_timestamp(time_str):
        minute, second, milis = list(map(int, time_str.split('-')))
        milis = milis + (1000 * second) + (60 * 1000 * minute)
        return milis

    @staticmethod
    def parse_duration(time_str, pattern='M-s-m'):
        second, milis = list(map(int, time_str.split('-')))
        milis = milis + (1000 * second)
        return milis

    @staticmethod
    def format_end_timestamp(formatted_start, formatted_duration):

        start_milis = TimeUtil.parse_timestamp(formatted_start)
        duration_milis = TimeUtil.parse_duration(formatted_duration)

        return TimeUtil.format_timestamp(start_milis + duration_milis)

