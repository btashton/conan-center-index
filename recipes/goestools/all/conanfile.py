from conans import ConanFile, CMake, tools
import os
import glob


class GoestoolsConan(ConanFile):
    name = "goestools"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/pietern/goestools"
    description = "Tools to work with signals and files from GOES satellites"
    topics = ("conan", "dsp", "sdr", "goes", "goestools")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
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
        pass

    def requirements(self):
        self.requires("proj/6.3.0")
        self.requires("librtlsdr/0.6.0")
        self.requires("nlohmann_json/3.7.3")
        self.requires("libaec/1.0.4")
        self.requires("libcorrect/20181010")
        self.requires("tinytoml/0.4@bincrafters/stable")
        self.requires("nanomsg/1.1.2@bincrafters/stable")
        self.requires("opencv/4.1.1@conan/stable")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob(self.name + "-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        tools.rmdir(os.path.join(self._source_subfolder, "vendor"))
        # tools.replace_in_file(os.path.join(self._source_subfolder, "src", "lib_proj.cmake"),
        #                       "include_directories(${CMAKE_SOURCE_DIR}/include)",
        #                       "include_directories(${PROJ4_SOURCE_DIR}/include)")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        #tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "dl", "m"]
