import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { title } from "@/components/primitives";
import DefaultLayout from "@/layouts/default";

export default function ResultsPage() {
  const [imgUrl, setImgUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("http://localhost:5000/result")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch result image");
        }
        return response.blob();
      })
      .then((blob) => {
        const url = URL.createObjectURL(blob);
        setImgUrl(url);
      })
      .catch((err) => {
        console.error(err);
        setError("Error fetching result image");
      });
  }, []);

  return (
    <DefaultLayout>
      <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
        <div className="inline-block max-w-lg text-center justify-center">
          <h1 className={title()}>Result Image</h1>
        </div>
        {error && <p className="text-red-500">{error}</p>}
        {imgUrl ? (
          <img src={imgUrl} alt="Result" className="max-w-md rounded shadow-md" />
        ) : (
          <p>Loading result image...</p>
        )}
        <button
          onClick={() => navigate("/process")}
          className="mt-4 px-4 py-2 text-white bg-blue-500 rounded shadow hover:bg-blue-600"
        >
          Back to Process
        </button>
      </section>
    </DefaultLayout>
  );
}
