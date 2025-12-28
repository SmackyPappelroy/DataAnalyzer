import { useEffect, useMemo, useState } from "react";

const API_BASE = "http://localhost:8000";

type Project = {
  project_id: string;
  name: string;
  description?: string;
  path: string;
};

type RecipeRunResponse = {
  status: string;
  logs: string[];
  outputs: string[];
};

const ProjectOverview = () => {
  const [projectName, setProjectName] = useState("Plant Project");
  const [projectDescription, setProjectDescription] = useState("Demo");
  const [project, setProject] = useState<Project | null>(null);
  const [statusMessage, setStatusMessage] = useState<string>("");
  const [datasets, setDatasets] = useState<string[]>([]);
  const [recipeList, setRecipeList] = useState<string[]>([]);
  const [selectedRecipe, setSelectedRecipe] = useState<string>("");
  const [recipeParams, setRecipeParams] = useState<string>('{"window":60,"threshold":3.0}');
  const [file, setFile] = useState<File | null>(null);
  const [datasetName, setDatasetName] = useState("import_data");
  const [fileType, setFileType] = useState("csv");
  const [recipeResult, setRecipeResult] = useState<RecipeRunResponse | null>(null);

  const canImport = useMemo(() => Boolean(project && file), [project, file]);
  const canRunRecipe = useMemo(() => Boolean(project && selectedRecipe), [project, selectedRecipe]);

  const createProject = async () => {
    setStatusMessage("Skapar projekt...");
    try {
      const response = await fetch(`${API_BASE}/api/projects`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: projectName, description: projectDescription }),
      });
      if (!response.ok) {
        throw new Error("Kunde inte skapa projekt.");
      }
      const data = (await response.json()) as Project;
      setProject(data);
      setStatusMessage(`Projekt skapat: ${data.name}`);
    } catch (error) {
      setStatusMessage((error as Error).message);
    }
  };

  const refreshDatasets = async (projectId: string) => {
    try {
      const response = await fetch(`${API_BASE}/api/datasets?project_id=${projectId}`);
      const data = (await response.json()) as { datasets: string[] };
      setDatasets(data.datasets);
    } catch {
      setDatasets([]);
    }
  };

  const refreshRecipes = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/recipes`);
      const data = (await response.json()) as { recipes: string[] };
      setRecipeList(data.recipes);
      if (!selectedRecipe && data.recipes.length > 0) {
        setSelectedRecipe(data.recipes[0]);
      }
    } catch {
      setRecipeList([]);
    }
  };

  useEffect(() => {
    refreshRecipes();
  }, []);

  useEffect(() => {
    if (project) {
      refreshDatasets(project.project_id);
    }
  }, [project]);

  const handleImport = async () => {
    if (!project || !file) {
      return;
    }
    setStatusMessage("Importerar fil...");
    const formData = new FormData();
    formData.append("project_id", project.project_id);
    formData.append("dataset_name", datasetName);
    formData.append("file", file);
    const endpoint = fileType === "excel" ? "/api/import/excel" : "/api/import/csv";
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        throw new Error("Importen misslyckades.");
      }
      await response.json();
      await refreshDatasets(project.project_id);
      setStatusMessage("Import klar.");
    } catch (error) {
      setStatusMessage((error as Error).message);
    }
  };

  const handleRunRecipe = async () => {
    if (!project || !selectedRecipe) {
      return;
    }
    setStatusMessage("Kör recept...");
    setRecipeResult(null);
    let params = {};
    try {
      params = JSON.parse(recipeParams);
    } catch {
      setStatusMessage("Fel i JSON-parametrar.");
      return;
    }
    try {
      const response = await fetch(`${API_BASE}/api/recipes/run?project_id=${project.project_id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ recipe_name: selectedRecipe, parameters: params }),
      });
      if (!response.ok) {
        throw new Error("Receptkörning misslyckades.");
      }
      const data = (await response.json()) as RecipeRunResponse;
      setRecipeResult(data);
      setStatusMessage("Recept klart.");
      await refreshDatasets(project.project_id);
    } catch (error) {
      setStatusMessage((error as Error).message);
    }
  };

  return (
    <section className="content">
      <header className="content__header">
        <div>
          <h2>MVP Workspace</h2>
          <p>Importera data, anslut databaser och kör recept lokalt.</p>
          {project ? (
            <p className="status">Aktivt projekt: {project.name}</p>
          ) : (
            <p className="status muted">Inget projekt valt ännu.</p>
          )}
        </div>
        <div className="actions">
          <button onClick={createProject}>New Project</button>
        </div>
      </header>

      <div className="panel-grid">
        <div className="panel">
          <h3>1. Skapa projekt</h3>
          <label>
            Projektnamn
            <input value={projectName} onChange={(event) => setProjectName(event.target.value)} />
          </label>
          <label>
            Beskrivning
            <input
              value={projectDescription}
              onChange={(event) => setProjectDescription(event.target.value)}
            />
          </label>
          <button onClick={createProject}>Skapa projekt</button>
        </div>

        <div className="panel">
          <h3>2. Importera fil</h3>
          <label>
            Dataset-namn
            <input value={datasetName} onChange={(event) => setDatasetName(event.target.value)} />
          </label>
          <label>
            Filtyp
            <select value={fileType} onChange={(event) => setFileType(event.target.value)}>
              <option value="csv">CSV/TSV</option>
              <option value="excel">Excel</option>
            </select>
          </label>
          <label>
            Fil
            <input type="file" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
          </label>
          <button onClick={handleImport} disabled={!canImport}>
            Importera fil
          </button>
        </div>

        <div className="panel">
          <h3>3. Kör recept</h3>
          <label>
            Recept
            <select value={selectedRecipe} onChange={(event) => setSelectedRecipe(event.target.value)}>
              {recipeList.map((recipe) => (
                <option key={recipe} value={recipe}>
                  {recipe}
                </option>
              ))}
            </select>
          </label>
          <label>
            Parametrar (JSON)
            <textarea
              rows={4}
              value={recipeParams}
              onChange={(event) => setRecipeParams(event.target.value)}
            />
          </label>
          <button onClick={handleRunRecipe} disabled={!canRunRecipe}>
            Run Recipe
          </button>
        </div>

        <div className="panel">
          <h3>Projektstatus</h3>
          <p className="status">{statusMessage || "Väntar på åtgärd..."}</p>
          <div className="dataset-list">
            <h4>Datasets</h4>
            <ul>
              {datasets.length === 0 ? (
                <li className="muted">Inga datasets ännu.</li>
              ) : (
                datasets.map((name) => <li key={name}>{name}</li>)
              )}
            </ul>
          </div>
          {recipeResult && (
            <div className="recipe-output">
              <h4>Receptresultat</h4>
              <p>Status: {recipeResult.status}</p>
              <p>Outputs: {recipeResult.outputs.join(", ") || "-"}</p>
              <div>
                <strong>Loggar</strong>
                <ul>
                  {recipeResult.logs.map((logLine, index) => (
                    <li key={`${logLine}-${index}`}>{logLine}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default ProjectOverview;
