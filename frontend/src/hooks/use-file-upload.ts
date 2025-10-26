import {
  useCallback,
  useRef,
  useState,
  type DragEvent,
  type ChangeEvent,
} from "react";

export interface FileUploadOptions {
  accept?: string;
  maxSize?: number;
  multiple?: boolean;
}

export interface FileUploadState {
  files: File[];
  isDragging: boolean;
  errors: string[];
}

export interface FileUploadActions {
  handleDragEnter: (e: DragEvent<HTMLElement>) => void;
  handleDragLeave: (e: DragEvent<HTMLElement>) => void;
  handleDragOver: (e: DragEvent<HTMLElement>) => void;
  handleDrop: (e: DragEvent<HTMLElement>) => void;
  handleFileChange: (e: ChangeEvent<HTMLInputElement>) => void;
  openFileDialog: () => void;
  clearFiles: () => void;
  removeFile: (fileName: string) => void;
  getInputProps: () => React.InputHTMLAttributes<HTMLInputElement>;
}

export const useFileUpload = (
  options: FileUploadOptions = {}
): [FileUploadState, FileUploadActions] => {
  const { accept = "*", maxSize = Infinity, multiple = false } = options;

  const [files, setFiles] = useState<File[]>([]);
  const [isDragging, setDragging] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  const validate = useCallback(
    (file: File) => {
      if (file.size > maxSize)
        return `File "${file.name}" exceeds ${formatBytes(maxSize)}.`;

      if (accept !== "*") {
        const acceptedTypes = accept.split(",").map((a) => a.trim());
        const ext = "." + file.name.split(".").pop()?.toLowerCase();
        const isValid = acceptedTypes.some((a) => {
          if (a.startsWith(".")) return a.toLowerCase() === ext;
          if (a.endsWith("/*")) return file.type.startsWith(a.split("/")[0]);
          return file.type === a;
        });
        if (!isValid) return `File "${file.name}" is not an accepted type.`;
      }
      return null;
    },
    [accept, maxSize]
  );

  const addFiles = useCallback(
    (incoming: FileList | File[]) => {
      const newFiles = Array.from(incoming);
      const newErrors: string[] = [];

      const valid = newFiles.filter((f) => {
        const err = validate(f);
        if (err) {
          newErrors.push(err);
          return false;
        }
        return true;
      });

      setFiles((prev) => (multiple ? [...prev, ...valid] : valid));
      setErrors(newErrors);
    },
    [multiple, validate]
  );

  const removeFile = useCallback((fileName: string) => {
    setFiles((prev) => prev.filter((f) => f.name !== fileName));
  }, []);

  const handleDragEnter = useCallback((e: DragEvent<HTMLElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent<HTMLElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(false);
  }, []);

  const handleDragOver = useCallback((e: DragEvent<HTMLElement>) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback(
    (e: DragEvent<HTMLElement>) => {
      e.preventDefault();
      e.stopPropagation();
      setDragging(false);
      if (e.dataTransfer.files.length > 0) addFiles(e.dataTransfer.files);
    },
    [addFiles]
  );

  const handleFileChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      if (e.target.files?.length) addFiles(e.target.files);
      if (inputRef.current) inputRef.current.value = "";
    },
    [addFiles]
  );

  const openFileDialog = useCallback(() => {
    inputRef.current?.click();
  }, []);

  const clearFiles = useCallback(() => setFiles([]), []);

  const getInputProps = useCallback(() => {
    return {
      ref: inputRef,
      type: "file",
      accept,
      multiple,
      onChange: handleFileChange,
    } as React.InputHTMLAttributes<HTMLInputElement>;
  }, [accept, multiple, handleFileChange]);

  return [
    { files, isDragging, errors },
    {
      handleDragEnter,
      handleDragLeave,
      handleDragOver,
      handleDrop,
      handleFileChange,
      openFileDialog,
      clearFiles,
      removeFile,
      getInputProps,
    },
  ];
};

const formatBytes = (bytes: number) => {
  const sizes = ["B", "KB", "MB", "GB"];
  if (bytes === 0) return "0 B";
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${parseFloat((bytes / Math.pow(1024, i)).toFixed(2))} ${sizes[i]}`;
};
