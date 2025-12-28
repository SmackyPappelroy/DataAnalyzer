import Sidebar from "./components/Sidebar";
import ProjectOverview from "./pages/ProjectOverview";

const App = () => {
  return (
    <div className="app">
      <Sidebar />
      <main className="main">
        <ProjectOverview />
      </main>
    </div>
  );
};

export default App;
