from sqlalchemy import Enum, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import enum
from .report import Base


class FileType(str, enum.Enum):
    pdf = "pdf"
    json = "json"
    txt = "txt"


class FileCategory(str, enum.Enum):
    source = "source"
    extract = "extract"
    output = "output"


class FileStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    error = "error"


class ReportFile(Base):
    __tablename__ = "report_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"))
    type: Mapped[FileType] = mapped_column(Enum(FileType, name="file_type"))
    category: Mapped[FileCategory] = mapped_column(
        Enum(FileCategory, name="file_category")
    )
    status: Mapped[FileStatus] = mapped_column(
        Enum(FileStatus, name="file_status"), default=FileStatus.pending
    )
    s3_bucket: Mapped[str] = mapped_column(Text)
    s3_key: Mapped[str] = mapped_column(Text)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    report = relationship("Report", back_populates="files")
