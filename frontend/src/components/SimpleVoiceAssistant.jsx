import {
  useVoiceAssistant,
  BarVisualizer,
  VoiceAssistantControlBar,
  useTrackTranscription,
  useLocalParticipant,
} from "@livekit/components-react";
import { Track } from "livekit-client";
import { useEffect, useState, useRef } from "react";
import "./SimpleVoiceAssistant.css";

const Message = ({ type, text }) => {
  return (
    <div className="message">
      <strong className={`message-${type}`}>
        {type === "agent" ? "Agent: " : "You: "}
      </strong>
      <span className="message-text">{text}</span>
    </div>
  );
};

const SimpleVoiceAssistant = () => {
  const { state, audioTrack, agentTranscriptions } = useVoiceAssistant();
  const localParticipant = useLocalParticipant();
  const { segments: userTranscriptions } = useTrackTranscription({
    publication: localParticipant.microphoneTrack,
    source: Track.Source.Microphone,
    participant: localParticipant.localParticipant,
  });

  const [messages, setMessages] = useState([]);
  const videoRef = useRef(null); // Ref for the video element
  const conversationRef = useRef(null); // Ref for the conversation container
  const streamRef = useRef(null); // Ref to store the media stream

  // Start camera feed
  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false, // Set to true if you want to capture audio as well
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          streamRef.current = stream;
        }
      } catch (error) {
        console.error("Error accessing camera:", error);
      }
    };

    startCamera();

    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop()); // Stop all tracks
      }
      if (videoRef.current) {
        videoRef.current.srcObject = null; // Clear the srcObject
      }
    };
  }, []);


  useEffect(() => {
    const allMessages = [
      ...(agentTranscriptions?.map((t) => ({ ...t, type: "agent" })) ?? []),
      ...(userTranscriptions?.map((t) => ({ ...t, type: "user" })) ?? []),
    ].sort((a, b) => a.firstReceivedTime - b.firstReceivedTime);
    setMessages(allMessages);
  }, [agentTranscriptions, userTranscriptions]);

  // Automatically scroll to the bottom when messages update
  useEffect(() => {
    if (conversationRef.current) {
      conversationRef.current.scrollTop = conversationRef.current.scrollHeight;
    }
  }, [messages]); // Trigger this effect whenever `messages` changes

  return (
    <div className="voice-assistant-container">
      {/* Main Content Section */}
      <div className="main-content">
        {/* Camera Feed Section */}
        <div className="video-container">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted // Mute the video to avoid feedback
            className="camera-feed"
          />
        </div>

        {/* Conversation Section */}
        <div className="conversation" ref={conversationRef} >
          {messages.map((msg, index) => (
            <Message key={msg.id || index} type={msg.type} text={msg.text} />
          ))}
        </div>
      </div>

      {/* Bar Visualizer Section */}
      <div className="visualizer-container">
        <BarVisualizer state={state} barCount={7} trackRef={audioTrack} />
      </div>

      {/* Control Bar Section */}
      <div className="control-section">
        <VoiceAssistantControlBar />
      </div>
    </div>
  );
};

export default SimpleVoiceAssistant;