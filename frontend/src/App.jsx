import { useState } from "react";
import "./App.css";
import LiveKitModal from "./components/LiveKitModal";

function App() {
  const [showSupport, setShowSupport] = useState(false);

  const handleSupportClick = () => {
    setShowSupport(true);
  };

  return (
    <div className="app">
      <header className="header">
        <div className="logo">IVA-Intelligent Virtual Assistant</div>
      </header>

      <main>
        <section className="IVA">
          <h1>
            Get Your Work Done. Right Now{" "}
            <span className="animated-icon icon-1">😅</span>
            <span className="animated-icon icon-2">😁</span>
          </h1>
          <h2>Just click on the Agent button !</h2>
          {/* <div className="search-bar">
            <input type="text" placeholder='Enter your Name'></input>
            <button>Search</button>
          </div> */}
        </section>
        <div className="motion-icon">
          <span className="arrow">👇</span> {/* Downward-pointing arrow */}
        </div>
        <button className="support-button" onClick={handleSupportClick}>
          Talk to the Agent!
        </button>
      </main>

      {showSupport && <LiveKitModal setShowSupport={setShowSupport} />}
    </div>
  );
}

export default App;
