export interface QueryResponse {
  sql: string;
  result: any;
  error?: string;
}

export interface SchemaInfo {
  columns: string[];
  types: { [key: string]: string };
  is_view: boolean;
  foreign_keys?: any[];
}

export interface DatabaseSchema {
  [tableName: string]: SchemaInfo;
} 