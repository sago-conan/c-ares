#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, shutil
from conans import ConanFile, CMake, tools


class CAresConan(ConanFile):
    name = "c-ares"
    version = "1.15.0"
    license = "MIT"
    url = "https://github.com/sago-conan/c-ares"
    description = "A C library for asynchronous DNS requests"
    homepage = "https://c-ares.haxx.se/"
    settings = "arch", "build_type", "compiler", "os"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_tools": False,
    }
    exports_sources = "ios.toolchain.cmake"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    @property
    def _folder_name(self):
        return "c-ares-{}".format(self.version)

    def source(self):
        url = "https://c-ares.haxx.se/download/{}.tar.gz".format(
            self._folder_name)
        tools.get(url)

    def build(self):
        cmake = CMake(self)
        # Build options
        cmake.definitions["CARES_STATIC"] = not self.options.shared
        cmake.definitions["CARES_SHARED"] = self.options.shared
        cmake.definitions["CARES_INSTALL"] = True
        if "fPIC" in self.options:
            cmake.definitions["CARES_STATIC_PIC"] = self.options.fPIC
        cmake.definitions["CARES_BUILD_TESTS"] = False
        cmake.definitions["CARES_BUILD_TOOLS"] = self.options.with_tools
        if self.settings.compiler == "Visual Studio":
            static_runtime = self.settings.compiler.runtime.startswith("MT")
            cmake.definitions["CARES_MSVC_STATIC_RUNTIME"] = static_runtime
        # Cross compile
        if self.settings.os == "Android":
            cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = os.path.join(
                os.environ["ANDROID_HOME"], "ndk-bundle", "build", "cmake",
                "android.toolchain.cmake")
        elif self.settings.os == "iOS":
            cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = os.path.join(
                self.source_folder, "ios.toolchain.cmake")
            if self.settings.arch == "armv8":
                cmake.definitions["IOS_PLATFORM"] = "OS64"
                cmake.definitions["IOS_ARCH"] = "arm64"
            elif self.settings.arch == "x86_64":
                cmake.definitions["IOS_PLATFORM"] = "SIMULATOR64"
                cmake.definitions["IOS_ARCH"] = "x86_64"
            cmake.definitions["ENABLE_BITCODE"] = False
            cmake.definitions["ENABLE_ARC"] = True
        self.output.info("CMake definitions: {}".format(cmake.definitions))
        # Build
        cmake.configure(source_folder=self._folder_name)
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
