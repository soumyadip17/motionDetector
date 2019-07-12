import cv2, os, simplejson as json
from confapp import conf
from pythonvideoannotator_module_contoursimages.contoursimages_window import ContoursImagesWindow


class Module(object):

    def __init__(self):
        """
        This implements the Path edition functionality
        """
        super(Module, self).__init__()

        
        self.contoursimages_window = ContoursImagesWindow(self)


        self.mainmenu[1]['Modules'].append(
            {"Extract the contour's images": self.contoursimages_window.show, 'icon':conf.ANNOTATOR_ICON_IMAGE },           
        )



    
    ######################################################################################
    #### IO FUNCTIONS ####################################################################
    ######################################################################################
    
    def save(self, data, project_path=None):
        data = super(Module, self).save(data, project_path)

        modules_folder = os.path.join(project_path, 'modules')
        if not os.path.exists(modules_folder): os.makedirs(modules_folder)

        module_folder = os.path.join(modules_folder, 'contoursimages')
        if not os.path.exists(module_folder): os.makedirs(module_folder)

        d = self.contoursimages_window.save_form({}, module_folder)

        with open(os.path.join(module_folder, 'config.json'), 'w') as outfile:
            json.dump(d, outfile)

        return data

    def load(self, data, project_path=None):
        super(Module, self).load(data, project_path)
        
        module_folder = os.path.join(project_path, 'modules', 'contoursimages')
        configfile = os.path.join(module_folder, 'config.json')

        if os.path.exists(configfile):

            with open(configfile) as infile:
                d = json.load(infile)

            self.contoursimages_window.load_form(d, module_folder)
