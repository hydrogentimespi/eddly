MENU root_menu
{
    LABEL [main_menu];
    ITEMS
    {
        configuration_menu,
        diagnostics_menu
    }
}

MENU configuration_menu
{
    LABEL [configuration_menu];
    ITEMS
    {
        sensor_value,
        sensor_unit
    }
}

MENU diagnostics_menu
{
    LABEL [diagnostics_menu];
    ITEMS
    {
        "device status",
        "process status"
    }
}

