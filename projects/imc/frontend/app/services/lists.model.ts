export interface UserList {
  uuid?: string;
  name: string;
  description: string;
  items?: ListItem[];
  belong?: boolean;
}

export interface ListItem {}
