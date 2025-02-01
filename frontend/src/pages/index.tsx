import React, { useRef, useState } from "react";
import { button as buttonStyles } from "@heroui/theme";
import { title } from "@/components/primitives";
import DefaultLayout from "@/layouts/default";
import { useNavigate } from "react-router-dom";

export default function IndexPage() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const personPicInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const [uploadedFilename, setUploadedFilename] = useState<string | null>(null);
  const [uploadedFilenameToRemove, setUploadedFilenameToRemove] = useState<string | null>(null);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleUploadPictureOfPersonClick = () => {
    personPicInputRef.current?.click();
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("main_pic", file); // key for regular image upload

    try {
      const response = await fetch("http://localhost:5123/upload", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      console.log(data);

      if (response.ok) {
        // Update the state with the uploaded file's filename
        setUploadedFilename(data.filename);
      } else {
        alert("File upload failed!");
      }
    } catch (error) {
      alert("An error occurred while uploading the file.");
    }
  };

  const handleFileChangePerson = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    // Use a different key to differentiate between upload types
    formData.append("person_pic", file);

    try {
      const response = await fetch("http://localhost:5123/upload", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      console.log(data);

      if (response.ok) {
        // Update the state with the uploaded person-picture filename
        setUploadedFilenameToRemove(data.filename);
      } else {
        alert("Person picture upload failed!");
      }
    } catch (error) {
      alert("An error occurred while uploading the person picture.");
    }
  };

  return (
    <DefaultLayout>
      <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
        <div className="inline-block max-w-lg text-center justify-center">
          <span className={title()}>Bluree</span>
          <br />
          <span className={title()}>Blurring faces in images</span>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleUploadClick}
            className={buttonStyles({
              color: "primary",
              radius: "full",
              variant: "shadow",
            })}
          >
            Upload Image
          </button>
          <button
            onClick={handleUploadPictureOfPersonClick}
            className={buttonStyles({
              color: "primary",
              radius: "full",
              variant: "shadow",
            })}
          >
            Upload picture of person to remove
          </button>
          <button
            onClick={() => navigate("/check")}
            className={buttonStyles({
              color: "primary",
              radius: "full",
              variant: "shadow",
            })}
          >
            Go to Processing Page
          </button>
          <input
            type="file"
            accept="image/*"
            ref={fileInputRef}
            onChange={handleFileChange}
            style={{ display: "none" }}
          />
          <input
            type="file"
            accept="image/*"
            ref={personPicInputRef}
            onChange={handleFileChangePerson}
            style={{ display: "none" }}
          />
        </div>
        {uploadedFilename && (
          <div className="mt-4">
            Uploaded file: <strong>{uploadedFilename}</strong>
          </div>
        )}
        {uploadedFilenameToRemove && (
          <div className="mt-4">
            Uploaded person picture: <strong>{uploadedFilenameToRemove}</strong>
          </div>
        )}
      </section>
    </DefaultLayout>
  );
}