export interface CustomUser {
  readonly declared_institution: string;
}

export interface File {
  creation: number;
  modification: number;
  name: string;
  size: number;
  type: string;
  status: string;
  status_message: string;
  /** @nullable */
  task_id: string;
  /** @nullable */
  warnings: string;
}

export interface Files extends Array<File> {}
