from git import Repo
import xml.etree.ElementTree
import re
from utils import remove_next_line, output_write, find_paths, get_samples
from utils.utils import print_status_samples, deal_with_empty_repo


def find_config_file(framework):
    if framework == "spring":
        return "pom.xml"
    if framework == "android":
        return "build.gradle"


def get_namespace(element):
    m = re.match('\{.*\}', element.tag)
    return m.group(0) if m else ''


def get_spring_version(path):
    try:
        arquivo = xml.etree.ElementTree.parse(path)
        namespace = get_namespace(arquivo.getroot())
        tag_versao = arquivo.find('./{0}parent/{0}version'.format(namespace)).text
        if "SNAPSHOT" in tag_versao:
            return ""
        return str(tag_versao)
    except:
        return ""


def get_android_version(path, key):
    try:
        version = ""
        with open(path) as file:
            for line in file:
                if key in line:
                    line = remove_next_line(line)
                    line = line.replace(" ", "")
                    line = line.replace("=", "")
                    version = line.split(key)[1]
                    if version == '"android-O"' or version == "'android-O'":
                        version = "26"
                    elif version == '"android-P"':
                        version = "28"
                    elif version == "'android-Q'":
                        version = "29"
            int(version)
            return str(version)
    except:
        return ""


def get_framework_version(framework, path, key):
    if framework == "spring":
        return get_spring_version(path)
    elif framework == "android":
        return get_android_version(path, key)


def write_output_header(configuration_file_key_words, framework):
    header = "framework,path"
    for config in configuration_file_key_words:
        header = header + "," + config
    output_write(framework, "currentframeworkversion", "currentframeworkversion", header, True)


def get_key_words(framework):
    if framework == "spring":
        return {"version": ""}
    elif framework == "android":
        return {"compileSdkVersion": "", "targetSdkVersion": "", "minSdkVersion": ""}


def checkout_default_branch_repository(sample):
    repository = Repo("repositories/" + sample)
    repository.git.checkout("master", "-f")


def currentframeworkversion(framework, projects):
    print("Computing current framework version")
    configuration_file = find_config_file(framework)
    configuration_file_key_words = get_key_words(framework)
    write_output_header(configuration_file_key_words, framework)
    samples = get_samples(projects)
    for index, sample in enumerate(samples):
        print_status_samples(index+1, len(samples))
        checkout_default_branch_repository(sample)
        deal_with_empty_repo(sample)
        configuration_files_paths = find_paths(configuration_file, "repositories/" + sample)
        for path in configuration_files_paths:
            output = framework + "," + path
            for key, value in configuration_file_key_words.items():
                version = get_framework_version(framework, path, key)
                output = output + "," + version
            if ",,," not in output and (framework != "spring" or "RELEASE" in output):
                output_write(framework, "currentframeworkversion", "currentframeworkversion", output, False)
