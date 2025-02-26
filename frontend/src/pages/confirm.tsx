import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { title } from "@/components/primitives";
import DefaultLayout from "@/layouts/default";

interface StateData {
  main_pic_bytes?: string;
  person_pic_bytes?: string;
  body_with_box_bytes?: string;
}

export default function ConfirmPage() {
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

  // Generic function to call the /check endpoint.
  async function handleConfirm() {
    try {
      const response = await fetch("http://localhost:5123/confirm_human", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
      });
      if (!response.ok) {
        throw new Error("Failed to confirm");
      } else {
        // Navigate to the "results" page after a successful call.
        navigate("/check");
      }
    } catch (err) {
      console.error(err);
      setError("Error confirming");
    }
  }

  return (
    <DefaultLayout>
      <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
        <div className="inline-block max-w-lg text-center">
          <h1 className={title()}>
            Detected Human Figures
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
            className="px-4 py-2 text-white bg-blue-500 rounded shadow hover:bg-blue-600"
            onClick={() => handleConfirm()}
          >
            Confirm
          </button>
        </div>
      </section>
    </DefaultLayout>
  );
}

