# Permission & Navigation Migration FAQ

## For End Users

### What's Changing?

We're improving the permission system and mobile navigation experience in TritIQ BOS. These changes are mostly behind the scenes and won't affect your day-to-day work.

### Do I Need to Do Anything?

**No action required!** The system will automatically handle the transition. You might notice:

- ✅ Faster permission checks
- ✅ Better mobile menu navigation
- ✅ More intuitive access control messages

### Common Questions

#### Q: Why can't I access a feature I could access before?

**A:** Your permissions haven't changed. If you experience access issues:

1. Try refreshing your browser (Ctrl+F5 or Cmd+Shift+R)
2. Log out and log back in
3. Contact your administrator if the issue persists

Your administrator may need to verify your role assignments.

#### Q: What does "Access Denied" mean?

**A:** It means you don't have the required permission for that action. The error message will now show:

```
Access Denied
You don't have permission to access this resource.
Required permission: inventory.read
Please contact your administrator to request access.
```

Contact your organization admin to request access.

#### Q: Why do some permissions show up differently now?

**A:** We've standardized how permissions are displayed. For example:
- Old: `inventory_read` or `inventory:read`
- New: `inventory.read`

The functionality is the same - just clearer to read.

#### Q: I'm on mobile and can't find a menu option

**A:** We've improved mobile navigation! Try:

1. **Tap the hamburger menu** (☰) in the top-left
2. **Use the search bar** at the top of the menu
3. **Expand sections** by tapping on them - all options are now accessible
4. **Quick access** - Dashboard, Email, and Tasks are always at the top

#### Q: Some menu items show a lock icon 🔒

**A:** This means the module is not enabled for your organization. Options:

1. **Contact your admin** to enable the module
2. **Upgrade your plan** if it's a premium feature
3. **Request a trial** for testing premium features

#### Q: What does the "Trial" badge mean?

**A:** Your organization is trying out a premium feature for free. After the trial:
- The feature may become locked
- Contact your admin to upgrade and continue using it

## For Administrators

### What's New for Admins?

#### 1. **Hierarchical Permissions**

Parent permissions now automatically grant child permissions:

Example: If you assign `master_data.read` to a role, users automatically get:
- `vendors.read`
- `products.read`
- `inventory.read`

This simplifies role management!

#### 2. **Better Permission Visibility**

In the Role Management page:
- Permissions now use clear dotted format
- Hierarchy is visualized
- Easier to understand what each role can do

#### 3. **Mobile Menu Improvements**

All modules and submodules are now accessible on mobile devices. Your mobile users can:
- Access every feature available on desktop
- Use improved search to find features quickly
- Navigate nested menus more easily

### Admin FAQ

#### Q: How do I assign permissions now?

**A:** No change to the process:

1. Go to **Settings → Role Management**
2. Select a role
3. Check permissions (now in clear dotted format)
4. Save changes

The system handles the rest!

#### Q: What permissions should I assign for common roles?

**Common Patterns:**

**Accountant Role:**
- `accounting.read` - View financial data
- `accounting.write` - Create/edit entries
- `voucher.read` - View vouchers
- `voucher.create` - Create vouchers

**Inventory Manager:**
- `master_data.read` - View all master data (includes vendors, products)
- `inventory.write` - Manage inventory
- `voucher.read` - View inventory vouchers

**Sales Representative:**
- `crm.read` - View customer data
- `crm.write` - Update customer records
- `sales.read` - View sales data
- `sales.create` - Create sales orders

#### Q: How do I enable a module for my organization?

1. Go to **Settings → Organization Settings**
2. Navigate to **Module Management**
3. Toggle modules on/off
4. Configure trial periods if needed

#### Q: A user reports they can't access something they should

**Troubleshooting Steps:**

1. **Check role permissions:**
   - Settings → Role Management
   - Verify the role has the required permission

2. **Check module entitlements:**
   - Settings → Organization Settings → Module Management
   - Ensure the module is enabled

3. **Verify user role assignment:**
   - Settings → User Management
   - Check the user's assigned role

4. **Check hierarchy:**
   - If they should have child permission, ensure parent is assigned
   - Example: `master_data.read` gives `vendors.read`

5. **Have user refresh:**
   - Clear cache (Ctrl+Shift+Delete)
   - Log out and back in

#### Q: Can I customize the permission hierarchy?

**A:** Not at this time. The hierarchy is defined at the system level to ensure consistency. Contact support if you have specific needs.

#### Q: What if I want more granular control?

**A:** Assign specific permissions instead of parent permissions:

Instead of: `master_data.read` (gives all child permissions)

Assign specific: `vendors.read` + `customers.read` (excludes `products.read`)

### Migration Tips for Admins

#### Before the Migration

1. **Review current role permissions** in Role Management
2. **Document your custom roles** and their permissions
3. **Note any access issues** users are experiencing

#### During the Migration

1. **Monitor the migration status** at Settings → System Info
2. **Watch for user reports** of access issues
3. **Check the migration logs** if available

#### After the Migration

1. **Verify key roles** still work as expected
2. **Test on mobile** to ensure navigation works
3. **Review audit logs** for any permission errors
4. **Update internal documentation** with new permission format

## Getting Help

### For Users

1. **Check this FAQ first**
2. **Contact your administrator** for access issues
3. **Use the in-app help** (? icon in top-right)

### For Administrators

1. **Review the Admin FAQ** above
2. **Check system logs** in Settings → Audit Logs
3. **Contact support** if issues persist:
   - Email: naughtyfruit53@gmail.com
   - Include: Organization ID, User details, Error messages

### Additional Resources

- [User Guide](../../USER_GUIDE.md)
- [RBAC Quick Start](../../RBAC_QUICKSTART.md)
- [Mobile UI Guide](../../docs/MOBILE_UI_GUIDE.md)

## Feedback

We value your feedback! If you have suggestions or encounter issues:

1. **Submit feedback** via Settings → Feedback
2. **Report bugs** with screenshots if possible
3. **Request features** through your admin

---

**Last Updated:** December 2024  
**Migration Status:** In Progress (Q1 2026)  
**Next Review:** Q2 2026 (Compatibility mode removal)
