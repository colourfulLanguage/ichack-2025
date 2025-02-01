import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { title } from "@/components/primitives";
import DefaultLayout from "@/layouts/default";

interface StateData {
  main_pic_bytes?: string;
  person_pic_bytes?: string;
  body_with_box_bytes?: string;
}

export default function CheckPage() {
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

  // Generic function to call the /check/processing endpoint.
  async function handleCheck(actionType: string) {
    try {
      const response = await fetch("http://localhost:5123/check", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ action: actionType }),
      });
      if (!response.ok) {
        throw new Error("Failed to blur/replace");
      } if (response.ok) {
        // Navigate to the "results" page after a successful call.
        navigate("/results");
      }
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
            Match the person in the image with the main image
          </h1>
        </div>
        {error && <p className="text-red-500">{error}</p>}
        {stateData ? (
          <div className="flex flex-col items-center gap-6">
            {stateData.body_with_box_bytes ? (
              <div className="flex flex-col items-center">
                <p>Main Image</p>
                <img
                  src={`data:image/jpeg;base64,${stateData.body_with_box_bytes}`}
                  alt="Main upload"
                  className="max-w-sm rounded shadow-md"
                />
              </div>
            ) : (
              <p>No main image uploaded</p>
            )}
            {stateData.person_pic_bytes ? (
              <div className="flex flex-col items-center">
                <p>Person Image</p>
                <img
                  src={`data:image/jpeg;base64,${stateData.person_pic_bytes}`}
                  alt="Person upload"
                  className="max-w-sm rounded shadow-md"
                />
              </div>
            ) : (
              <p>No person image uploaded</p>
            )}
          </div>
        ) : (
          <p>Loading state...</p>
        )}

        <div className="flex flex-row gap-4 mt-8">
          <button
            className="px-4 py-2 text-white bg-blue-500 rounded shadow hover:bg-blue-600"
            onClick={() => handleCheck("yes")}
          >
            Found the person
          </button>
          <button
            className="px-4 py-2 text-white bg-blue-500 rounded shadow hover:bg-blue-600"
            onClick={() => handleCheck("no")}
          >
            Not same
          </button>
        </div>
      </section>
    </DefaultLayout>
  );
}

