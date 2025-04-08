import pandas as pd
from pathlib import Path

def fetch_annotation(annotation_path: str) -> Path:
    """Fetch the annotation file from the specified path.

    Parameters
    ----------
    annotation_path : str
        The path to the annotation file.

    Returns
    -------
    Path
        The path to the fetched annotation file.
    """
    annotation_path = Path(annotation_path).expanduser()
    if not annotation_path.exists():
        raise FileNotFoundError(f"Annotation file not found: {annotation_path}")
    frame = pd.read_excel(annotation_path)
    return frame