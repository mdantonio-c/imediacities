import { Injectable } from "@angular/core";

export enum Permission {
  ACCESS_CONTENT,
  CREATE_ANNOTATION,
}

@Injectable()
export class AuthzService {
  constructor() {}

  /**
   * Check user permission for ACCESS_CONTENT (default) or CREATE_ANNOTATION.
   * Permission depends also on media right status.
   * @param user to whom the permission is to be granted. Must not be null.
   * @param media for which permissions should be checked. Must not be null.
   * @param permission a representation of the permission type. Defaults to ACCESS_CONTENT.
   * @return true if the permission is granted, false otherwise
   */
  hasPermission(user, media, permission = Permission.ACCESS_CONTENT) {
    if (!user) {
      console.warn("the user must be provided to check permissions");
      return false;
    }
    if (!media) {
      console.warn("the media target must be provided to check permissions");
      return false;
    }
    /*console.log('has permission user?', user);
		console.log('check permission to media', media);*/
    switch (permission) {
      case Permission.ACCESS_CONTENT: {
        /*console.log('check permission to ACCESS_CONTENT');*/
        return this.isGeneralPublic(user) && !this.isPublicDomain(media)
          ? false
          : true;
      }
      case Permission.CREATE_ANNOTATION: {
        /*console.log('check permission to CREATE ANNOTATION');*/
        return !this.isGeneralPublic(user) ||
          (this.isGeneralUser(user) && this.isPublicDomain(media))
          ? true
          : false;
      }
      default: {
        console.warn("Invalid permission choice", permission);
        break;
      }
    }
    return false;
  }

  private isPublicDomain(media) {
    if (!media) return false;
    let k = media.rights_status.key;

    // EU Orphan Work
    if (k == "02") return true;

    // In copyright - Non-commercial use permitted
    if (k == "04") return true;

    // Public Domain
    if (k == "05") return true;

    // No Copyright - Contractual Restrictions
    if (k == "06") return true;

    // No Copyright - Non-Commercial Use Only
    if (k == "07") return true;

    // No Copyright - Other Known Legal Restrictions
    if (k == "08") return true;

    // No Copyright - United States
    if (k == "09") return true;

    return false;
  }

  private isGeneralUser(user) {
    // logged in user with role 'normal_user'
    if (!user) return false;
    return user.roles && user.roles.normal_user ? true : false;
  }

  private isGeneralPublic(user) {
    // both anonymous and general users
    return !user || this.isGeneralUser(user) ? true : false;
  }
}
