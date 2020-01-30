from conans import ConanFile, CMake, tools
import os


class LibrtlsdrConan(ConanFile):
    name = "librtlsdr"
    license = "GPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://osmocom.org/projects/rtl-sdr/wiki/Rtl-sdr"
    description = "Adaptive Entropy Coding library"
    topics = ("conan", "dsp", "librtlsdr", "sdr", "radio")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "detach_kernel_driver": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "detach_kernel_driver": True,
    }

    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt", "patches/*"]

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.detach_kernel_driver

    def requirements(self):
        self.requires("libusb/1.0.23")
        if self.settings.os == "Windows":
            self.requires("pthreads4w/3.0.0")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "rtl-sdr-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if self.settings.os == "Linux":
            self._cmake.definitions["DETACH_KERNEL_DRIVER"] = self.options.detach_kernel_driver
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        tools.patch(**self.conan_data["patches"][self.version])
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "find_package(LibUSB)",
                              "find_package(libusb)")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "m", "rt"]
        if self.settings.os == "Macos":
            self.cpp_info.system_libs = ["pthread", "m"]
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.libs.extend(["ws2_32"])
