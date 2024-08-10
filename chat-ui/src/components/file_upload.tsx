import React, { useState, useEffect, useMemo, ChangeEvent } from "react";
import { CloudUploadIcon, Trash2Icon, FileIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

export function FileUploadUI() {
  const [documentData, setDocumentData] = useState([]);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    fetchDocuments();
    const interval = setInterval(fetchDocuments, 2000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await fetch("http://localhost:8000/document");
      if (!response.ok) throw new Error("Failed to fetch documents");
      const data = await response.json();
      setDocumentData((prevData) => {
        if (JSON.stringify(prevData) !== JSON.stringify(data)) {
          return data;
        }
        return prevData;
      });
    } catch (error) {
      console.error("Error fetching documents:", error);
    }
  };

  const documents = useMemo(() => documentData, [documentData]);

  const handleFileUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const file = files[0];

    setIsUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/document/upload", {
        method: "POST",
        body: formData,
      });
      if (!response.ok) throw new Error("Failed to upload file");
      await fetchDocuments(); // Refresh the list after upload
    } catch (error) {
      console.error("Error uploading file:", error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (fileName: string) => {
    try {
      const response = await fetch(
        `http://localhost:8000/document/${fileName}`,
        {
          method: "DELETE",
        }
      );
      if (!response.ok) throw new Error("Failed to delete file");
      await fetchDocuments(); // Refresh the list after deletion
    } catch (error) {
      console.error("Error deleting file:", error);
    }
  };

  return (
    <div className="flex h-full flex-col">
      <header className="sticky top-0 z-10 border-b bg-background px-6 py-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium">Document Upload</h3>
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" asChild>
              <label htmlFor="file-upload">
                <CloudUploadIcon className="h-5 w-5" />
                <input
                  id="file-upload"
                  type="file"
                  className="hidden"
                  onChange={handleFileUpload}
                  disabled={isUploading}
                />
              </label>
            </Button>
          </div>
        </div>
      </header>
      <div className="flex-1 overflow-auto p-6">
        {documents.length === 0 ? (
          <EmptyUpload />
        ) : (
          <FilledUpload documents={documents} onDelete={handleDelete} />
        )}
      </div>
    </div>
  );
}

interface Document {
  file_name: string;
  status: string;
}

function FilledUpload({
  documents,
  onDelete,
}: {
  documents: Document[];
  onDelete: (fileName: string) => Promise<void>;
}) {
  return (
    <div className="grid gap-4">
      {documents.map((doc) => (
        <div
          key={doc.file_name}
          className="flex items-center justify-between rounded-lg bg-muted p-4"
        >
          <div className="flex items-center gap-4">
            <FileIcon className="h-6 w-6 text-muted-foreground" />
            <div>
              <div className="font-medium">{doc.file_name}</div>
              <div className="text-sm text-muted-foreground">{doc.status}</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => onDelete(doc.file_name)}
            >
              <Trash2Icon className="h-5 w-5" />
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
}

function EmptyUpload() {
  return (
    <div className="flex h-full items-center justify-center">
      <div className="grid max-w-md gap-4 text-center">
        <CloudUploadIcon className="mx-auto h-12 w-12 text-muted-foreground" />
        <h4 className="text-2xl font-bold">Upload Documents</h4>
        <p className="text-muted-foreground">
          Drag and drop your documents here or click to upload.
        </p>
        <Button variant="secondary" asChild>
          <label htmlFor="file-upload">
            Upload Documents
            <input id="file-upload" type="file" className="hidden" />
          </label>
        </Button>
      </div>
    </div>
  );
}
