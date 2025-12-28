const ProjectOverview = () => {
  return (
    <section className="content">
      <header className="content__header">
        <div>
          <h2>MVP Workspace</h2>
          <p>Importera data, anslut databaser och kör recept lokalt.</p>
        </div>
        <div className="actions">
          <button>New Project</button>
          <button>Import File</button>
          <button>Run Recipe</button>
        </div>
      </header>

      <div className="grid">
        <div className="card">
          <h3>Preview</h3>
          <p>Förhandsvisning av importen med schema och typdetektion.</p>
        </div>
        <div className="card">
          <h3>Schema & tags</h3>
          <p>Normalisera tidsstämplar, enheter och kolumnklassning.</p>
        </div>
        <div className="card">
          <h3>Visualization</h3>
          <p>Interaktiva tidsserier med zoom, pan och events.</p>
        </div>
        <div className="card">
          <h3>Recipe editor</h3>
          <p>Python-kod med parameterpanel, körlogg och artifacts.</p>
        </div>
      </div>
    </section>
  );
};

export default ProjectOverview;
