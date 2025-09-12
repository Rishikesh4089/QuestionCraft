import React from "react";

interface Props {
  files: File[];
  onFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onRemoveFile: (fileName: string) => void;
  onUpload: (file: any) => void;
}

const FileUploadSection: React.FC<Props> = ({ files, onFileChange, onRemoveFile }) => (
  <div className="mb-6">
    <label className="block text-lg font-medium text-slate-700 mb-2">1. Upload Study Materials</label>
    <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-slate-300 border-dashed rounded-md">
      <div className="space-y-1 text-center">
        <input
          id="file-upload"
          name="file-upload"
          type="file"
          className="sr-only"
          multiple
          onChange={onFileChange}
        />
        <label
          htmlFor="file-upload"
          className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500"
        >
          Upload files
        </label>
        <p className="text-xs text-slate-500">PDF, PPTX up to 10 files</p>
      </div>
    </div>

    {files.length > 0 && (
      <ul className="mt-4 space-y-2">
        {files.map((file, index) => (
          <li
            key={index}
            className="flex items-center justify-between bg-slate-100 p-2 rounded-md text-sm"
          >
            <span className="truncate">{file.name}</span>
            <button
              onClick={() => onRemoveFile(file.name)}
              className="text-red-500 hover:text-red-700"
            >
              ✕
            </button>
          </li>
        ))}
      </ul>
    )}
  </div>
);

export default FileUploadSection;
