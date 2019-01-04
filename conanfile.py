#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
from conans.errors import ConanException
import os


class LibnameConan(ConanFile):
    name = "corrade"
    version = "2018.10"
    description =   "Corrade is a multiplatform utility library written \
                    in C++11/C++14. It's used as a base for the Magnum \
                    graphics engine, among other things."
    # topics can get used for searches, GitHub topics, Bintray tags etc. Add here keywords about the library
    topics = ("conan", "corrad", "magnum", "filesystem", "console", "environment", "os")
    url = "https://github.com/helmesjo/conan-corrade"
    homepage = "https://magnum.graphics/corrade"
    author = "helmesjo <helmesjo@gmail.com>"
    license = "MIT"  # Indicates license type of the packaged library; please use SPDX Identifiers https://spdx.org/licenses/
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    short_paths = True  # Some folders go out of the 260 chars path length scope (windows)

    # Options may need to change depending on the packaged library.
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False], 
        "fPIC": [True, False],
        "build_deprecated": [True, False],
        "build_tests": [True, False],
        "with_interconnect": [True, False],
        "with_pluginmanager": [True, False],
        "with_testsuite": [True, False],
    }
    default_options = {
        "shared": False, 
        "fPIC": True,
        "build_deprecated": False,
        "build_tests": False,
        "with_interconnect": True,
        "with_pluginmanager": True,
        "with_testsuite": False,
    }

    # Custom attributes for Bincrafters recipe conventions
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = (
    )

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

        if self.options.build_tests:
            self.options.with_testsuite = True

    def configure(self):
        if self.settings.compiler == 'Visual Studio' and int(self.settings.compiler.version.value) < 14:
            raise ConanException("{} requires Visual Studio version 14 or greater".format(self.name))

    def source(self):
        source_url = "https://github.com/mosra/corrade"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version

        # Rename to "source_subfolder" is a convention to simplify later steps
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)

        def add_cmake_option(option, value):
            var_name = "{}".format(option).upper()
            value_str = "{}".format(value)
            var_value = "ON" if value_str == 'True' else "OFF" if value_str == 'False' else value_str 
            cmake.definitions[var_name] = var_value

        for attr, _ in self.options.iteritems():
            value = getattr(self.options, attr)
            add_cmake_option(attr, value)

        add_cmake_option("BUILD_STATIC", not self.options.shared)

        if self.settings.compiler == 'Visual Studio':
            add_cmake_option("MSVC2015_COMPATIBILITY", int(self.settings.compiler.version.value) == 14)
            add_cmake_option("MSVC2017_COMPATIBILITY", int(self.settings.compiler.version.value) == 17)
        
        if self.settings.compiler == 'gcc':
            add_cmake_option("GCC47_COMPATIBILITY", float(self.settings.compiler.version.value) < 4.8)

        cmake.configure(build_folder=self._build_subfolder)

        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    # Fix later. Currently root contains no tests, and source_subfolder fails to run the test (can't find executables)
#        if self.options.build_tests:
            # self.output.info("Running {} tests".format(self.name))
            # source_path = os.path.join(self._build_subfolder, self._source_subfolder)
            # with tools.chdir(source_path):
            #     self.run("ctest --build-config {}".format(self.settings.build_type))

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # If the CMakeLists.txt has a proper install method, the steps below may be redundant
        # If so, you can just remove the lines below
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="*", dst="include", src=include_folder)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.options.build_deprecated:
            self.cpp_info.defines.append("CORRADE_BUILD_DEPRECATED")