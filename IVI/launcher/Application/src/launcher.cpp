// Use kanzi.hpp only when you are learning to develop Kanzi applications.
// To improve compilation time in production projects, include only the header files of the Kanzi functionality you are using.
#include <kanzi/kanzi.hpp>

// [CodeBehind libs inclusion]. Do not remove this identifier.

#if defined(DEMO_CODE_BEHIND_API) && !defined(ANDROID) && !defined(KANZI_API_IMPORT)
# include <demo_code_behind_module.hpp>
#endif

#if defined(COMMON_CODE_BEHIND_API) && !defined(ANDROID) && !defined(KANZI_API_IMPORT)
# include <common_code_behind_module.hpp>
#endif

#if defined(CAR_SETTING_CODE_BEHIND_API) && !defined(ANDROID) && !defined(KANZI_API_IMPORT)
# include <car_setting_code_behind_module.hpp>
#endif

#if defined(ENVIRONMENT_CODE_BEHIND_API) && !defined(ANDROID) && !defined(KANZI_API_IMPORT)
# include <environment_code_behind_module.hpp>
#endif

#if defined(LAUNCHER_CODE_BEHIND_API) && !defined(ANDROID) && !defined(KANZI_CORE_API_IMPORT)
#include <launcher_code_behind_module.hpp>
#endif

using namespace kanzi;

class Launcher : public ExampleApplication
{
public:

    void onConfigure(ApplicationProperties& configuration) override
    {
        configuration.binaryName = "launcher.kzb.cfg";
    }

    void onProjectLoaded() override
    {
        // Project file has been loaded from .kzb file.

        // Add initialization code here.
    }

    void registerMetadataOverride(ObjectFactory& factory) override
    {
        ExampleApplication::registerMetadataOverride(factory);

#if defined(LAUNCHER_CODE_BEHIND_API) && !defined(ANDROID) && !defined(KANZI_CORE_API_IMPORT)
        LauncherCodeBehindModule::registerModule(getDomain());
#endif

        // [CodeBehind module inclusion]. Do not remove this identifier.

#if defined(DEMO_CODE_BEHIND_API) && !defined(ANDROID) && !defined(KANZI_API_IMPORT)
        DemoCodeBehindModule::registerModule(getDomain());
#endif

#if defined(COMMON_CODE_BEHIND_API) && !defined(ANDROID) && !defined(KANZI_API_IMPORT)
        CommonCodeBehindModule::registerModule(getDomain());
#endif

#if defined(CAR_SETTING_CODE_BEHIND_API) && !defined(ANDROID) && !defined(KANZI_API_IMPORT)
        CarSettingCodeBehindModule::registerModule(getDomain());
#endif

#if defined(ENVIRONMENT_CODE_BEHIND_API) && !defined(ANDROID) && !defined(KANZI_API_IMPORT)
        EnvironmentCodeBehindModule::registerModule(getDomain());
#endif
    }
};

Application* createApplication()
{
    return new Launcher;
}
