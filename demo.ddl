/********************************************
*
*   EDDLY demonstration
*
********************************************/

MANUFACTURER 255, DEVICE_TYPE 38911, DEVICE_REVISION 1, DD_REVISION 1


#if ENABLE_MENUES==1
#include "demo_menu.ddl"
#endif

VARIABLE sensor_value
{
    LABEL [sensor_value_string];
    CLASS LOCAL & DYNAMIC;
    HANDLING READ & WRITE;
    TYPE FLOAT;
}

VARIABLE sensor_unit
{
    CLASS LOCAL & DYNAMIC;
    HANDLING READ & WRITE;
    TYPE UNSIGNED_INTEGER(1);
}

COMMAND write_configuration
{
    NUMBER 555;
    OPERATION WRITE;
    TRANSACTION
    {
        REQUEST
        {
            config_data
        }
    }
}

