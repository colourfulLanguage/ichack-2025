import React, { useRef, useState, useEffect } from "react";
import { button as buttonStyles } from "@heroui/theme";
import { Button } from "@heroui/react";
import { title } from "@/components/primitives";
import DefaultLayout from "@/layouts/default";
import { useNavigate } from "react-router-dom";
import groupPic from "@/components/images/group_pic.png";
import indPic from "@/components/images/ind_pic.png"

export default function IndexPage() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const personPicInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const [uploadedFilename, setUploadedFilename] = useState<string | null>(null);
  const [uploadedFilenameToRemove, setUploadedFilenameToRemove] = useState<string | null>(null);

  const [previewImage, setPreviewImage] = useState<string | null>(null);
  const [previewImageToRemove, setPreviewImageToRemove] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

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

        const file = event.target.files?.[0];
        if (!file) return;
        const imageUrl = URL.createObjectURL(file);
        setPreviewImage(imageUrl);
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

        const file = event.target.files?.[0];
        if (!file) return;
        const imageUrl = URL.createObjectURL(file);
        setPreviewImageToRemove(imageUrl);
      } else {
        alert("Person picture upload failed!");
      }
    } catch (error) {
      alert("An error occurred while uploading the person picture.");
    }
  };

  // New function to call the /human_detection endpoint before navigating
  const handleHumanDetection = async () => {
    try {
      setIsLoading(true);
      const response = await fetch("http://localhost:5123/human_detection", {
        method: "POST",
      });
      if (response.ok) {
        navigate("/confirm");
      } else {
        alert("Human detection request failed!");
      }
    } catch (error) {
      alert("An error occurred during human detection.");
    }
  };

  const handleRasperry = async () => {
    try {
      // const response = await fetch("http://localhost:5123/human_detection", {
      //   method: "POST",
      // });
      // if (response.ok) {
      // } else {
      //   alert("Human detection request failed!");
      // }
      // System.log("Rasperry")
    } catch (error) {
      // alert("An error occurred during human detection.");
    }
  }

  return (
    <DefaultLayout>
      <section className="image-button gap-20 py-8 md:py-10">
        <div className="inline-block max-w-lg text-center justify-center">
          <span className={`${title()} text-3xl`}>Bluree</span>
        </div>
        <section className="h-screen flex flex-col justify-center items-center snap-start">
          <h1 className="text-5xl font-bold">
            Process and modify images. <br />
            Opt-out people aware. <br />
            Take control.</h1>
          <p className="text-lg mt-5 text-center max-w-lg">Use Bluree</p>
          <button onClick={handleRasperry} className="custom-button">Get Images From Device</button>
          <div className="mt-40"></div> {/* Added space */}
          <div className="mt-40 absolute bottom-10 animate-bounce text-sm">Scroll Down ↓</div>
        </section>

        <section className="h-screen flex flex-col justify-center items-center gap-10 snap-start">
          <div className="flex gap-3">
            <div className="flex flex-col items-center gap-20">
              <div className="flex justify-center gap-40">
                <div className="image-button">
                  <button onClick={handleUploadClick} className="circular-button" style={{ "--button-size": "20rem", "--translate-y": "15px", "--width": "130%", "--height": "150%" } as React.CSSProperties}>
                    <img src={previewImage || groupPic} alt="Upload Image" />
                  </button>
                  <p className="image-text">Upload Image</p>
                </div>

                <div className="image-button">
                  <button onClick={handleUploadPictureOfPersonClick} className="circular-button" style={{ "--button-size": "14rem", "--translate-x": "-2px", "--width": "300%", "--height": "220%" } as React.CSSProperties}>
                    <img src={previewImageToRemove || indPic} alt="Upload Ind Image" className="w-60 h-70 object-contain cursor-pointer hover:opacity-80" />
                  </button>
                  <p className="image-text">Upload person to remove</p>
                </div>
              </div>

              <Button
                onClick={handleHumanDetection}
                isLoading={isLoading}
                className="custom-button">
                Go to Processing Page
              </Button>

            </div>
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
        </section>
      </section>
    </DefaultLayout>
  );
}