import os
import stat
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field
import mimetypes

# ===============================
# Pydantic Models
# ===============================

class PathLibMetadata(BaseModel):
    """מטא-דטה מ-pathlib"""
    name: str = Field(description="שם הקובץ")
    stem: str = Field(description="שם הקובץ ללא סיומת")
    suffix: str = Field(description="סיומת הקובץ")
    suffixes: list[str] = Field(description="כל הסיומות")
    parent: str = Field(description="תיקיה מכילה")
    parts: list[str] = Field(description="חלקי הנתיב")
    is_file: bool = Field(description="האם זה קובץ")
    is_dir: bool = Field(description="האם זה תיקיה")
    exists: bool = Field(description="האם קיים")
    is_absolute: bool = Field(description="נתיב מוחלט")

class OSMetadata(BaseModel):
    """מטא-דטה מ-os"""
    size_bytes: int = Field(description="גודל בבייטים")
    size_mb: float = Field(description="גודל ב-MB")
    created_timestamp: float = Field(description="זמן יצירה (timestamp)")
    modified_timestamp: float = Field(description="זמן שינוי אחרון (timestamp)")
    accessed_timestamp: float = Field(description="זמן גישה אחרון (timestamp)")
    created_datetime: datetime = Field(description="זמן יצירה")
    modified_datetime: datetime = Field(description="זמן שינוי אחרון")
    accessed_datetime: datetime = Field(description="זמן גישה אחרון")
    permissions: str = Field(description="הרשאות")
    owner_uid: int = Field(description="UID של הבעלים")
    group_gid: int = Field(description="GID של הקבוצה")
    inode: int = Field(description="Inode number")
    mime_type: Optional[str] = Field(description="MIME type")
    encoding: Optional[str] = Field(description="Encoding")

class AudioFileHash(BaseModel):
    """Hash של הקובץ"""
    md5: str = Field(description="MD5 hash")
    sha256: str = Field(description="SHA256 hash")
    file_hash_short: str = Field(description="8 תווים ראשונים של SHA256")

class CombinedAudioMetadata(BaseModel):
    """כל המטא-דטה המשולב"""
    file_path: str = Field(description="נתיב הקובץ המלא")
    pathlib_data: PathLibMetadata
    os_data: OSMetadata
    file_hash: AudioFileHash
    extraction_timestamp: datetime = Field(description="מתי חולץ המטא-דטה")

# ===============================
# Extraction Functions
# ===============================

def get_pathlib_metadata(file_path: Union[str, Path]) -> PathLibMetadata:
    """מחלץ מטא-דטה דרך pathlib"""
    path = Path(file_path)
    
    return PathLibMetadata(
        name=path.name,
        stem=path.stem,
        suffix=path.suffix,
        suffixes=path.suffixes,
        parent=str(path.parent),
        parts=list(path.parts),
        is_file=path.is_file(),
        is_dir=path.is_dir(),
        exists=path.exists(),
        is_absolute=path.is_absolute()
    )

def get_os_metadata(file_path: Union[str, Path]) -> OSMetadata:
    """מחלץ מטא-דטה דרך os"""
    path_str = str(file_path)
    
    # קבלת stat info
    stat_info = os.stat(path_str)
    
    # המרת timestamps לdatetime
    created_dt = datetime.fromtimestamp(stat_info.st_ctime)
    modified_dt = datetime.fromtimestamp(stat_info.st_mtime)
    accessed_dt = datetime.fromtimestamp(stat_info.st_atime)
    
    # MIME type
    mime_type, encoding = mimetypes.guess_type(path_str)
    
    return OSMetadata(
        size_bytes=stat_info.st_size,
        size_mb=round(stat_info.st_size / (1024 * 1024), 2),
        created_timestamp=stat_info.st_ctime,
        modified_timestamp=stat_info.st_mtime,
        accessed_timestamp=stat_info.st_atime,
        created_datetime=created_dt,
        modified_datetime=modified_dt,
        accessed_datetime=accessed_dt,
        permissions=stat.filemode(stat_info.st_mode),
        owner_uid=stat_info.st_uid,
        group_gid=stat_info.st_gid,
        inode=stat_info.st_ino,
        mime_type=mime_type,
        encoding=encoding
    )

def calculate_file_hashes(file_path: Union[str, Path]) -> AudioFileHash:
    """מחשב hash של הקובץ"""
    path_str = str(file_path)
    
    md5_hash = hashlib.md5()
    sha256_hash = hashlib.sha256()
    
    # קריאת הקובץ בחלקים (לקבצים גדולים)
    with open(path_str, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
            sha256_hash.update(chunk)
    
    sha256_full = sha256_hash.hexdigest()
    
    return AudioFileHash(
        md5=md5_hash.hexdigest(),
        sha256=sha256_full,
        file_hash_short=sha256_full[:8]
    )

def get_combined_audio_metadata(file_path: Union[str, Path]) -> CombinedAudioMetadata:
    """מחלץ את כל המטא-דטה במשולב"""
    
    # וולידציה בסיסית
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"קובץ לא נמצא: {file_path}")
    
    if not path.is_file():
        raise ValueError(f"הנתיב אינו מוביל לקובץ: {file_path}")
    
    # חילוץ כל המטא-דטה
    pathlib_data = get_pathlib_metadata(path)
    os_data = get_os_metadata(path)
    file_hash = calculate_file_hashes(path)
    
    return CombinedAudioMetadata(
        file_path=str(path.absolute()),
        pathlib_data=pathlib_data,
        os_data=os_data,
        file_hash=file_hash,
        extraction_timestamp=datetime.now()
    )

# ===============================
# Usage Examples
# ===============================

if __name__ == "__main__":
    file_path = r"C:\podcasts\download (6).wav"
    
    try:
        # מטא-דטה נפרד
        print("=== PathLib Metadata ===")
        pathlib_meta = get_pathlib_metadata(file_path)
        print(pathlib_meta.model_dump_json(indent=2, ensure_ascii=False))
        
        print("\n=== OS Metadata ===")
        os_meta = get_os_metadata(file_path)
        print(os_meta.model_dump_json(indent=2, ensure_ascii=False))
        
        print("\n=== File Hashes ===")
        hashes = calculate_file_hashes(file_path)
        print(hashes.model_dump_json(indent=2, ensure_ascii=False))
        
        print("\n=== Combined Metadata ===")
        combined = get_combined_audio_metadata(file_path)
        print(combined.model_dump_json(indent=2, ensure_ascii=False))
        
        # השימוש בתור dictionary
        metadata_dict = combined.model_dump()
        print(f"\nגודל קובץ: {metadata_dict['os_data']['size_mb']} MB")
        print(f"Hash קצר: {metadata_dict['file_hash']['file_hash_short']}")
        
    except Exception as e:
        print(f"שגיאה: {e}")
