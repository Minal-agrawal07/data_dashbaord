const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function req<T>(method: string, path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}
export const api = {
  getSchema: () => req<{ files: SchemaFile[] }>("GET", "/api/schema"),

  refreshSchema: () =>
    req<{ files: SchemaFile[] }>("POST", "/api/schema/refresh"),




  verifyAccessKey: (key: string) =>
  req<{ valid: boolean }>("POST", "/api/verify-key", {
    key,
  }),  

  
  uploadCSV: async (file: File, accessKey: string = "") => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("access_key", accessKey);
  
    const res = await fetch(`${BASE}/api/upload`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Upload failed" }));
      throw new Error(err.detail || "Upload failed");
    }

    return res.json();
  },



  generateDashboard: (filename: string) =>
  req<{ cards: any[] }>("POST", "/api/dashboard/generate", {
    filename,
  }),


  
  generateChart: (body: GenerateRequest) =>
    req<GenerateResponse>("POST", "/api/charts/generate", body),

  refineChart: (chartId: number, body: RefineRequest) =>
    req<GenerateResponse>("POST", `/api/charts/${chartId}/refine`, body),

  runSQL: (sql: string, nlQuery?: string) =>
    req<GenerateResponse>("POST", "/api/charts/run-sql", {
      sql,
      nl_query: nlQuery,
    }),

  getCharts: (dashboardId?: number) =>
    req<{ charts: Chart[] }>(
      "GET",
      `/api/charts${dashboardId ? `?dashboard_id=${dashboardId}` : ""}`
    ),

  getDashboards: () =>
    req<{ dashboards: Dashboard[] }>("GET", "/api/dashboards"),

  createDashboard: (name: string) =>
    req<Dashboard>("POST", "/api/dashboards", { name }),

  updateLayout: (dashboardId: number, layout_config: LayoutItem[]) =>
    req("PUT", `/api/dashboards/${dashboardId}/layout`, { layout_config }),

  health: () =>
    req<{ status: string; csv_files: number; model_path_set: boolean }>(
      "GET",
      "/api/health"
    ),
};
export interface SchemaFile {
  id: number;
  filename: string;
  row_count: number;
  columns: {
    column_name: string;
    data_type: string;
    sample_values: string[];
    description?: string;
  }[];
}

export interface GenerateRequest {
  nl_query: string;
  conversation_history?: ConversationTurn[];
  dashboard_id?: number;
}

export interface RefineRequest {
  nl_query: string;
  chart_id: number;
  conversation_history?: ConversationTurn[];
}

export interface ConversationTurn {
  role: "user" | "assistant";
  content: string;
  sql?: string;
}

export interface GenerateResponse {
  clarification_needed?: boolean;
  question?: string;
  chart_id?: number;
  sql?: string;
  chart_type?: string;
  chart_config?: Record<string, unknown>;
  row_count?: number;
  data?: Record<string, unknown>[];
  intent?: Record<string, unknown>;
}

export interface Chart {
  id: number;
  dashboard_id?: number;
  nl_query: string;
  sql_query?: string;
  chart_config?: Record<string, unknown>;
  conversation_history?: ConversationTurn[];
}

export interface Dashboard {
  id: number;
  name: string;
  layout_config?: LayoutItem[];
}

export interface LayoutItem {
  i: string;
  x: number;
  y: number;
  w: number;
  h: number;
}
