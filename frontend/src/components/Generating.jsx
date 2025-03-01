import { call, watch } from "../assets";

const Generating = ({ className }) => {
  return (
    <div className={`flex justify-between ${className || ""}`}>
      {/* Left Side */}
      <div className="flex items-center h-[3.5rem] px-6 bg-n-8/80 rounded-[1.7rem] text-base">
        Next Question
      </div>
      <div className="flex items-center h-[3.5rem] px-10 rounded-[1.7rem] text-base ">
        <img className="w-15 h-15 ml-7 mr-5" src={call} alt="Loading" />
      </div>
      {/* Right Side */}
      <div className="flex items-center h-[3.5rem] px-6 bg-n-8/80 rounded-[1.7rem] text-base">
        <img className="w-8 h-8 mr-4" src={watch} alt="Loading" />
        30:00
      </div>
    </div>
  );
};

export default Generating;
