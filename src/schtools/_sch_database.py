import os
import shutil
import time
import warnings

from datetime import datetime
from os import environ, makedirs
from os.path import expanduser, join
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.error import URLError
from urllib.request import urlretrieve

import pandas as pd

REMOTE_SCH_DATASET = {
    "url": "https://www.anatel.gov.br/dadosabertos/paineis_de_dados/certificacao_de_produtos",
    "filename": "produtos_certificados.zip",
}


def _get_data_home(data_home=None) -> str:
    """Return the path of the data directory.

    By default the data directory is set to a folder named 'sch_database' in the
    user home folder.

    Alternatively, it can be set by the 'SCH_DATAHOME' environment
    variable or programmatically by giving an explicit folder path.
    The '~' symbol is expanded to the user home folder.

    If the folder does not already exist, it is automatically created.

    Parameters
    ----------
    data_home : str or path-like, default=None
        The path to data directory. If `None`, the default path
        is `%LOCALAPPDATA%/Local/sch_database` or `~/sch_database`.

    Returns
    -------
    data_home: path-like
        The path to data directory.

    """
    default_data_home = join(os.environ.get("LOCALAPPDATA", "~"), "sch_database")
    if data_home is None:
        data_home = environ.get("SCH_DATAHOME", default_data_home)
    data_home = expanduser(data_home)

    return Path(data_home)


def _download_sch_database(
    target_dir,
    n_retries=3,
    delay=1,
):
    """Helper function to download SCH remote dataset.

    Fetch SCH dataset pointed by remote's url, save into path using remote's
    filename.

    Parameters
    ----------
    target_dir : path-like.
        Directory to save the file to. The path to data directory.

    n_retries : int, default=3
        Number of retries when HTTP errors are encountered.

    delay : int, default=1
        Number of seconds between retries.

    Returns
    -------
    file_path: Path
        Full path of the created file.
    """

    makedirs(target_dir, exist_ok=True)
    sch_file_path = target_dir / REMOTE_SCH_DATASET["filename"]

    temp_file = NamedTemporaryFile(
        prefix=REMOTE_SCH_DATASET["filename"] + ".part_", dir=target_dir, delete=False
    )
    temp_file.close()

    try:
        temp_file_path = Path(temp_file.name)
        while True:
            try:
                url = REMOTE_SCH_DATASET["url"] + "/" + REMOTE_SCH_DATASET["filename"]
                urlretrieve(url, temp_file_path)
                break
            except (URLError, TimeoutError):
                if n_retries == 0:
                    # If no more retries are left, re-raise the caught exception.
                    raise
                warnings.warn(
                    f"Retry downloading from url: {REMOTE_SCH_DATASET['url']}"
                )
                n_retries -= 1
                time.sleep(delay)
    except (Exception, KeyboardInterrupt):
        os.unlink(temp_file.name)
        raise

    # The following renaming is atomic whenever temp_file_path and
    # file_path are on the same filesystem. This should be the case most of
    # the time, but we still use shutil.move instead of os.rename in case
    # they are not.
    shutil.move(temp_file_path, sch_file_path)
    if not sch_file_path.exists():
        raise OSError("Error downloading SCH Database file.")


def fetch_sch_database(
    *,
    data_home=None,
    download_if_missing=True,
    download_grace_period=180,
    force_download=False,
    n_retries=3,
    delay=1.0,
):
    """Load data from SCH dataset

    Download it if necessary.

    Parameters
    ----------
    data_home : str or path-like, default = None
        Specify a download and cache folder for the datasets. If None,
        all the data is stored in '~/sch_database' subfolder.

    download_if_missing : bool, default=True
        If False, raise an OSError if the data is not locally available
        instead of trying to download the data from the source site.

    download_grace_period : int, default=180
        Specify the number of days that must pass before re-download
        the file from the internet.

    force_download : bool, default=False
        If True, re-download the file from the internet.

    n_retries : int, default=3
        Number of retries when HTTP errors are encountered.

    delay : float, default=1.0
        Number of seconds between retries.

    Returns
    -------
    frame : DataFrame of shape (n, 21)

        columns
    ==  ===========================================
    0   Data da Homologação
    1   Número de Homologação
    2   Nome do Solicitante
    3   CNPJ do Solicitante
    4   Certificado de Conformidade Técnica
    5   Data do Certificado de Conformidade Técnica
    6   Data de Validade do Certificado
    7   Código de Situação do Certificado
    8   Situação do Certificado
    9   Código de Situação do Requerimento
    10  Situação do Requerimento
    11  Nome do Fabricante
    12  Modelo
    13  Nome Comercial
    14  Categoria do Produto
    15  Tipo do Produto
    16  IC_ANTENA
    17  IC_ATIVO
    18  País do Fabricante
    19  CodUIT
    20  CodISO
    ==  ===========================================

    """
    if data_home is None:
        data_home = _get_data_home(data_home=data_home)
    else:
        data_home = Path(data_home)

    sch_file_path = data_home / REMOTE_SCH_DATASET["filename"]

    if sch_file_path.exists():
        # Check if the file is older than the grace period
        sch_file_ctime = datetime.fromtimestamp(sch_file_path.stat().st_mtime)
        sch_file_age = datetime.today() - sch_file_ctime
        if sch_file_age.days > download_grace_period:
            print(
                f"File {sch_file_path} is older than {download_grace_period} days. "
                "Re-downloading the file..."
            )
            _download_sch_database(data_home, n_retries=n_retries, delay=delay)
        elif force_download:
            # If the file is not older than the grace period and force_download is True, download it
            print(
                f"File {sch_file_path} is not older than {download_grace_period} days. "
                "Re-downloading the file (forced)..."
            )
            _download_sch_database(data_home, n_retries=n_retries, delay=delay)
    else:
        if download_if_missing:
            # If the file does not exist and download_if_missing is True, download it
            print(f"File {sch_file_path} does not exist. Downloading the file...")
            _download_sch_database(data_home, n_retries=n_retries, delay=delay)
        else:
            # If the file does not exist and download_if_missing is False, raise an error
            raise OSError(
                f"File {sch_file_path} does not exist. Set download_if_missing=True to download it."
            )

    # Read the file into a DataFrame
    dtype = {
        "Número de Homologação": str,
        "CNPJ do Solicitante": str,
    }
    frame = pd.read_csv(sch_file_path, sep=";", dtype=dtype)

    # Convert the date columns to datetime
    frame["Data da Homologação"] = pd.to_datetime(
        frame["Data da Homologação"], format="%d/%m/%Y", errors="coerce"
    )
    frame["Data do Certificado de Conformidade Técnica"] = pd.to_datetime(
        frame["Data do Certificado de Conformidade Técnica"],
        format="%d/%m/%Y",
        errors="coerce",
    )
    frame["Data de Validade do Certificado"] = pd.to_datetime(
        frame["Data de Validade do Certificado"],
        format="%d/%m/%Y %H:%M:%S",
        errors="coerce",
    )

    # remove rows with null values in the 'Número de Homologação' column
    frame = frame.dropna(subset=["Número de Homologação"])
    
    return frame
