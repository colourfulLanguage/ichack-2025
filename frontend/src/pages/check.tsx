import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { title } from "@/components/primitives";
import DefaultLayout from "@/layouts/default";

interface StateData {
  main_pic_bytes?: string;
  person_pic_bytes?: string;
  body_with_box_bytes?: string;
  similarity_score?: number | 0;
  any_more_faces?: number;
}

export default function CheckPage() {
  const [stateData, setStateData] = useState<StateData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const [triggerCount, setTriggerCount] = useState(0);

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
  }, [triggerCount]);

  // Generic function to call the /check/processing endpoint.

  async function handleGetNext() {
    // Reload page
    console.log("Im in get next!!")
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
        // navigate("/check");
        setTriggerCount(triggerCount + 1);
      }
    } catch (err) {
      console.error(err);
      setError("Error confirming");
    }
  }

  async function handleCheck() {
    try {
      const response = await fetch("http://localhost:5123/found_person", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
      });
      if (!response.ok) {
        throw new Error("Failed to get the person");
      } if (response.ok) {
        navigate("/process");
      }
    } catch (err) {
      console.error(err);
      setError("Error in finding person");
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
            <p>Similarity score : {(stateData.similarity_score * 100).toFixed(2)}%</p>
          </div>
        ) : (
          <p>Loading state...</p>
        )}
        {stateData?.any_more_faces === 0 ? (
          <div>
            <p> The person is not there! </p>
            <button
              className="px-4 py-2 text-white bg-blue-500 rounded shadow hover:bg-blue-600"
              onClick={() => navigate("/")}
            >
              Go back to home
            </button>
          </div>
        ) : (
          <div className="flex flex-row gap-4 mt-8">
            <button
              className="px-4 py-2 text-white bg-blue-500 rounded shadow hover:bg-blue-600"
              onClick={() => handleCheck()}
            >
              Found the person
            </button>
            <button
              className="px-4 py-2 text-white bg-blue-500 rounded shadow hover:bg-blue-600"
              onClick={() => handleGetNext()}
            >
              Not same
            </button>
          </div>
        )
        }
      </section>
    </DefaultLayout>
  );
}

