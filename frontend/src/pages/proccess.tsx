import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { title } from "@/components/primitives";
import DefaultLayout from "@/layouts/default";

interface StateData {
  main_pic_bytes?: string;
  person_pic_bytes?: string;
  body_with_box_bytes?: string;
}

export default function ProcessPage() {
  const [stateData, setStateData] = useState<StateData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Call the local API endpoint to retrieve state.
    fetch("http://localhost:5123/get_state")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch state");
        }
        return response.json();
      })
      .then((data: StateData) => {
        setStateData(data);
      })
      .catch((err) => {
        console.error(err);
        setError("Error fetching state");
      });
  }, []);


  // Generic function to call the /modify endpoint.
  async function handleModify(actionType: string) {
    try {
      const response = await fetch("http://localhost:5123/modify", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ action: actionType }),
      });
      if (!response.ok) {
        throw new Error("Failed to blur/replace");
      }
      // Navigate to the "results" page after a successful call.
      navigate("/results");
    } catch (err) {
      console.error(err);
      setError("Error blurring/replacing");
    }
  }

  return (
    <DefaultLayout>
      <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
        <div className="inline-block max-w-lg text-center">
          <h1 className={title()}>
            How to Process the Image
          </h1>
        </div>
        {error && <p className="text-red-500">{error}</p>}
        {stateData ? (
          <div className="flex flex-col items-center gap-6">
            {stateData.body_with_box_bytes ? (
              <div className="flex flex-col items-center">
                <img
                  src={`data:image/jpeg;base64,${stateData.body_with_box_bytes}`}
                  alt="Main upload"
                  className="max-w-xl rounded-xl shadow-2xl border-5 border-white-400 transform hover:scale-105 transition-transform duration-300 ease-in-out"
                />
              </div>
            ) : (
              <p>No main image uploaded</p>
            )}

          </div>
        ) : (
          <p>Loading state...</p>
        )}

        <div className="flex flex-row gap-4 mt-8">
          <button
            className="custom-button"
            onClick={() => handleModify("blur")}
          >
            Blur
          </button>
          <button
            className="custom-button"
            onClick={() => handleModify("sticker")}
          >
            Put Sticker on it!
          </button>
        </div>
      </section>
    </DefaultLayout>
  );
}
