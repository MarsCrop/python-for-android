from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.logger import shprint, info
from pythonforandroid.util import current_directory
from multiprocessing import cpu_count
from os.path import join
import os
import glob
import sh
import shutil


class NumpyRecipe(CompiledComponentsPythonRecipe):

    #version = '1.9.3'
    version = '1.18.1'    
    #version = '1.23.3'
    url = 'https://pypi.python.org/packages/source/n/numpy/numpy-{version}.zip'
    #url = 'https://pypi.python.org/packages/source/n/numpy/numpy-{version}.tar.gz'
    site_packages_name = 'numpy'
    depends = ['setuptools', 'cython', 'hostpython3']
    #install_in_hostpython = True
    install_in_hostpython = False
    call_hostpython_via_targetpython = False
    #call_hostpython_via_targetpython = True

    patches = [
        join("patches", "add_libm_explicitly_to_build.patch"),
        join("patches", "ranlib.patch"),
        join("patches", "fix_empty_doc_error_on_import.patch"),
        join("patches", "remove-default-paths.patch"), 
        join('patches', 'hostnumpy-xlocale.patch'),
        join('patches', 'compiler_cxx_fix.patch'),        
    ]
   

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        #PYTHON VENV (HOSTPYTHON) IS DECLARED DURING DEPENDENCIES DOWNLOAD
        env = super().get_recipe_env(arch, with_flags_in_cc)

        # _PYTHON_HOST_PLATFORM declares that we're cross-compiling
        # and avoids issues when building on macOS for Android targets.
        env["_PYTHON_HOST_PLATFORM"] = arch.command_prefix

        # NPY_DISABLE_SVML=1 allows numpy to build for non-AVX512 CPUs
        # See: https://github.com/numpy/numpy/issues/21196
        env["NPY_DISABLE_SVML"] = "1"
        hostpython = sh.Command(self.hostpython_location)                    
        os.system("wget https://bootstrap.pypa.io/get-pip.py")
        shprint(hostpython, "get-pip.py", "install")
        shprint(hostpython, "-m", "pip", "install", "setuptools")                    
        shprint(hostpython, "-m", "pip", "install", "cython")      
        return env

    def _build_compiled_components(self, arch):
        #PYTHON VENV (HOSTPYTHON) IS DECLARED DURING DEPENDENCIES DOWNLOAD
        info('Building compiled components in {}'.format(self.name))

        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            hostpython = sh.Command(self.hostpython_location)
            shprint(hostpython, 'setup.py', self.build_cmd, '-v',
                    _env=env, *self.setup_extra_args)
            build_dir = glob.glob('build/lib.*')[0]
            shprint(sh.find, build_dir, '-name', '"*.o"', '-exec',
                    env['STRIP'], '{}', ';', _env=env)
            hostpython = sh.Command(self.hostpython_location)                    
            os.system("wget https://bootstrap.pypa.io/get-pip.py")
            shprint(hostpython, "get-pip.py", "install")
            shprint(hostpython, "-m", "pip", "install", "setuptools")                    
        shprint(hostpython, "-m", "pip", "install", "cython")      

    def _rebuild_compiled_components(self, arch, env):
        info('Rebuilding compiled components in {}'.format(self.name))
        #PYTHON VENV (HOSTPYTHON) IS DECLARED DURING DEPENDENCIES DOWNLOAD
        hostpython = sh.Command(self.real_hostpython_location)
        shprint(hostpython, 'setup.py', 'clean', '--all', '--force', _env=env)
        shprint(hostpython, 'setup.py', self.build_cmd, '-v', _env=env,
                *self.setup_extra_args)
        os.system("wget https://bootstrap.pypa.io/get-pip.py")
        shprint(hostpython, "get-pip.py", "install")
        shprint(hostpython, "-m", "pip", "install", "setuptools")                 
        shprint(hostpython, "-m", "pip", "install", "cython")      
        
    def build_compiled_components(self, arch):
        #PYTHON VENV (HOSTPYTHON) IS DECLARED DURING DEPENDENCIES DOWNLOAD
        self.setup_extra_args = ['-j', str(cpu_count())]
        self._build_compiled_components(arch)
        self.setup_extra_args = []
        hostpython = sh.Command(self.hostpython_location)                    
        os.system("wget https://bootstrap.pypa.io/get-pip.py")
        shprint(hostpython, "get-pip.py", "install")
        shprint(hostpython, "-m", "pip", "install", "setuptools")                    
        shprint(hostpython, "-m", "pip", "install", "cython")          

    def rebuild_compiled_components(self, arch, env):
        #PYTHON VENV (HOSTPYTHON) IS DECLARED DURING DEPENDENCIES DOWNLOAD
        self.setup_extra_args = ['-j', str(cpu_count())]
        self._rebuild_compiled_components(arch, env)
        self.setup_extra_args = []
        hostpython = sh.Command(self.hostpython_location)                    
        os.system("wget https://bootstrap.pypa.io/get-pip.py")
        shprint(hostpython, "get-pip.py", "install")
        shprint(hostpython, "-m", "pip", "install", "setuptools")                    
        shprint(hostpython, "-m", "pip", "install", "cython")      

    def get_hostrecipe_env(self, arch):
        env = super().get_hostrecipe_env(arch)
        env['RANLIB'] = shutil.which('ranlib')
        return env


recipe = NumpyRecipe()

