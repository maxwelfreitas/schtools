from ._sch import fetch_sch_database
from ._annotation import fetch_annotation
from os.path import join


class SCHToolsDatasets:
    """
    A class to manage the download and extraction of schematic datasets.

    Attributes
    ----------
    remote_sch_dataset : dict
        A dictionary containing the URL and filename of the remote dataset.
    local_sch_dataset : str
        The path to the local dataset directory.
    """

    def __init__(self, config):
        # get the path to the data home directory
        # self.data_home = Path(config['datasets']['data_home'])
        # self.sch_data_home = Path(config['datasets']['sch_data_home'])
        # self.search_results_data_home = Path(config['datasets']['search_results_data_home'])
        # self.annotation_data_home = Path(config['datasets']['annotation_data_home'])
        # self.cloud_annotation_get_folder = Path(config['cloud']['cloud_annotation_get_folder'])
        # self.cloud_annotation_post_folder = Path(config['cloud']['cloud_annotation_post_folder'])

        self.sch = fetch_sch_database(config["datasets"]["sch_data_home"])
        cloud_annotation_get_file = join(
            config["cloud"]["cloud_annotation_get_folder"], "Annotation.xlsx"
        )
        self.annotation = fetch_annotation(cloud_annotation_get_file)
