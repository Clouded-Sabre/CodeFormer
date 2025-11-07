import os
import subprocess
import time

version_file = 'version.py'  # Relative path (same dir)

def get_git_hash():
    def _minimal_ext_cmd(cmd):
        env = {}
        for k in ['SYSTEMROOT', 'PATH', 'HOME']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env).communicate()[0]
        return out
    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        sha = out.strip().decode('ascii')
    except OSError:
        sha = 'unknown'
    return sha

def get_hash():
    if os.path.exists('.git'):
        sha = get_git_hash()[:7]
    elif os.path.exists(version_file):
        try:
            from version import __version__
            sha = __version__.split('+')[-1]
        except ImportError:
            raise ImportError('Unable to get git version')
    else:
        sha = 'unknown'
    return sha

def write_version_py():
    content = """# GENERATED VERSION FILE
# TIME: {}
__version__ = '{}'
__gitsha__ = '{}'
version_info = ({})
"""
    sha = get_hash()
    # Debug: Check if VERSION file exists
    if not os.path.exists('VERSION'):
        print("Error: 'VERSION' file not found in current directory.")
        return
    with open('VERSION', 'r') as f:  # Corrected relative path
        SHORT_VERSION = f.read().strip()
    VERSION_INFO = ', '.join([x if x.isdigit() else f'"{x}"' for x in SHORT_VERSION.split('.')])
    version_file_str = content.format(time.asctime(), SHORT_VERSION, sha, VERSION_INFO)
    with open(version_file, 'w') as f:
        f.write(version_file_str)

if __name__ == '__main__':
    write_version_py()
    # Debug: Confirm generation
    if os.path.exists(version_file):
        print(f"{version_file} generated successfully.")
    else:
        print(f"Failed to generate {version_file}.")