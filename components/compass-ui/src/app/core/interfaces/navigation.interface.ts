export interface BaseNavigationItem {
  label: string;
  icon: string;
}

export interface InternalNavigationItem extends BaseNavigationItem {
  path: string;
}

export interface ExternalNavigationItem extends BaseNavigationItem {
  url: string;
  target?: string;
}

export interface SubMenuNavigationItem extends BaseNavigationItem {
  items: (InternalNavigationItem | ExternalNavigationItem)[];
}

export type NavigationItem =
  | InternalNavigationItem
  | ExternalNavigationItem
  | SubMenuNavigationItem;
