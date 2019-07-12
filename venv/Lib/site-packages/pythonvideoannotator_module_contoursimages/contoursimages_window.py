import pyforms, math, cv2, os, numpy as np
from confapp import conf
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlNumber
from pyforms.controls import ControlList
from pyforms.controls import ControlCombo
from pyforms.controls import ControlDir
from pyforms.controls import ControlSlider
from pyforms.controls import ControlButton
from pyforms.controls import ControlCheckBox
from pyforms.controls import ControlCheckBoxList
from pyforms.controls import ControlEmptyWidget
from pyforms.controls import ControlProgress
from pyforms.controls import ControlToolBox
from pyforms.controls import ControlBoundingSlider

from pythonvideoannotator_models_gui.dialogs import DatasetsDialog
from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.contours import Contours
from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.path import Path

import simplejson as json

from pythonvideoannotator_models.utils.tools import points_angle, rotate_image





class ContoursImagesWindow(BaseWidget):

    def __init__(self, parent=None):
        super(ContoursImagesWindow, self).__init__('Contour images', parent_win=parent)
        self.mainwindow = parent

        self.set_margin(5)
        

        self.setMinimumHeight(400)
        self.setMinimumWidth(800)

        self._contourspanel = ControlEmptyWidget('Contours datasets')
        self._progress      = ControlProgress('Progress', visible=False)       
        self._apply         = ControlButton('Apply', checkable=True)
        self._toolbox       = ControlToolBox('Toolbox')
        self._exportdir     = ControlDir('Export images to folder', default='images-from-contour')
        

        #### mask ######################################################
        self._usemaskimg       = ControlCheckBox('Apply a mask to the image')
        self._usemaskdilate    = ControlCheckBox('Dilate the mask and apply it to the image')
        self._maskdilatesize   = ControlSlider('Dilate size', default=0, minimum=0, maximum=100)
        self._usemaskellipse   = ControlCheckBox('Apply the min. ellipse as a mask to the image')
        self._usemaskcircular  = ControlCheckBox('Apply a circular mask to the image')
        self._maskcircularsize = ControlSlider('Circular radius', default=0, minimum=0, maximum=100)
        self._usemaskrect      = ControlCheckBox('Apply the min. rect as a mask to the image')
        ################################################################

        #### margin ####################################################
        self._margin = ControlSlider('Margin size', default=0, minimum=0, maximum=100)
        ################################################################

        #### imagesize #################################################
        self._imagesize = ControlSlider('Image size', default=0, minimum=0, maximum=400)
        ################################################################

        #### cut #######################################################
        self._usecut = ControlCheckBox('Cut image')
        self._cutx = ControlBoundingSlider('X cut', default=(10,30), minimum=0, maximum=1000)
        self._cuty = ControlBoundingSlider('Y cut', default=(10,30), minimum=0, maximum=1000)
        ################################################################
        

        #### use stretch ###############################################
        self._usestretch = ControlCheckBox('Stretch image')
        ################################################################

        #### filter per events #########################################
        self._eventslst  = ControlCheckBoxList('Events', enabled=True)
        self._reloadevts = ControlButton('Reload events', enabled=True, default=self.__reload_events_btn_evt)
        ################################################################

        #### rotation ##################################################
        self._userotup          = ControlCheckBox('Turn the contour always up')
        self._userotdown        = ControlCheckBox('Turn the contour always down')
        self._usefixedangle     = ControlCheckBox('Use a fixed orientation')
        self._fixedangle        = ControlSlider('Rotate the images using a fixed angle', enabled=True, default=0, minimum=0, maximum=360)
        self._usedatasetangle   = ControlCheckBox('Use the orientation of other contour')
        self._datasetanglepanel = ControlEmptyWidget('Datasets for the orientation', enabled=True)
        ################################################################

        #### image position ############################################
        self._useposdataset   = ControlCheckBox('Use a dataset to center the image')
        self._datasetpospanel = ControlEmptyWidget('Datasets for the image position', enabled=True)
        ################################################################

        
        self.formset = [
            '_toolbox',
            '_exportdir',
            '_apply',
            '_progress'
        ]

        self.load_order = [
            '_contourspanel','_userotup', '_userotdown',
            '_exportdir','_usemaskimg','_usemaskdilate','_usemaskellipse','_usemaskellipse',
            '_usemaskcircular', '_maskcircularsize', '_usemaskrect', '_margin', '_imagesize',
            '_usestretch', '_eventslst', '_usefixedangle', '_fixedangle', '_usedatasetangle',
            '_datasetanglepanel', '_useposdataset', '_datasetpospanel', '_usecut', '_cuty', '_cutx'
        ]

        #datasets painel
        self.datasets_dialog = DatasetsDialog(self)
        self.datasets_dialog.datasets_filter = lambda x: isinstance(x, Contours )
        self._contourspanel.value = self.datasets_dialog

        self.posdatasets_dialog = DatasetsDialog(self)
        self.posdatasets_dialog.datasets_filter = lambda x: isinstance(x, (Contours,Path) )
        self._datasetpospanel.value = self.posdatasets_dialog

        self.orientdatasets_dialog = DatasetsDialog(self)
        self.orientdatasets_dialog.datasets_filter = lambda x: isinstance(x, Contours )
        self.orientdatasets_dialog.interval_visible = False
        self._datasetanglepanel.value = self.orientdatasets_dialog


        self._apply.value       = self.__apply_event
        self._apply.icon        = conf.ANNOTATOR_ICON_PATH

        self._imagesize.changed_event = self.__image_size_changed_evt

        self._toolbox.value = [
            ('Extract from contours',(
                self.datasets_dialog,
            )),
            ('Mask',(
                self._usemaskimg,
                (self._usemaskdilate,self._maskdilatesize),
                (self._usemaskcircular,self._maskcircularsize),
                (self._usemaskellipse,self._usemaskrect),
            )),
            ('Margin, image size and stretch image',(
                self._usestretch,
                self._margin, 
                self._imagesize,
                self._usecut,
                self._cutx,
                self._cuty
            )),
            ('Rotate images',(
                (self._userotup, self._userotdown),
                (self._usefixedangle, self._fixedangle),
                self._usedatasetangle,
                self._datasetanglepanel
            )),
            ('Center images',(
                self._useposdataset,
                self._datasetpospanel,
            )),
            ('Export images per events',(
                self._reloadevts,
                self._eventslst,
            )),
        ]

        self.__reload_events_btn_evt()
        self.__image_size_changed_evt()

    ###########################################################################
    ### EVENTS ################################################################
    ###########################################################################

    def __image_size_changed_evt(self):
        if self._imagesize.value>0:
            self._usecut.enabled = True
            self._cutx.enabled = True
            self._cuty.enabled = True
            self._cuty.max = self._imagesize.value
            self._cutx.max = self._imagesize.value
        else:
            self._usecut.enabled = False
            self._cutx.enabled = False
            self._cuty.enabled = False

    def __reload_events_btn_evt(self):
        """
        Find all the events available on the timeline
        """
        timeline = self.mainwindow.timeline
        rows     = timeline.rows

        events   = {}
        for row in rows:
            for event in row.events:
                events[event.title] = True

        events = sorted(events.keys())

        loaded_events = dict(self._eventslst.items)
        self._eventslst.value = [(e, loaded_events.get(e, False)) for e in events]


  
    ###########################################################################
    ### PROPERTIES ############################################################
    ###########################################################################

    @property
    def datasets(self): return self.datasets_dialog.datasets
    

    @property
    def player(self): return self._filter._player


    def __get_events_cuts(self, begin, end):
        ### calculate the video cuts #############################
        selected_events = self._eventslst.value
        videocuts       = []
        if len(selected_events):
            # use the events to cut the video
            totalframes = 0
            timeline    = self.mainwindow.timeline

            for row in timeline.rows:
                for event in row.events:
                    if event.end<=begin: continue
                    if event.begin>=end: continue
                    if event.title not in selected_events: continue
                    b = int(event.begin if event.begin>=begin else begin)
                    e = int(event.end   if event.end<=end else end)
                    totalframes += e-b
                    videocuts.append( (b, e, event.title) )
            videocuts = sorted(videocuts, key = lambda x: x[0])
        else:
            # no events were selected
            totalframes = end-begin
            videocuts   = [(int(begin), int(end), None)]
        ##########################################################
        return videocuts

    def __get_export_map(self, begin_frame, end_frame, eventscuts):
        """
        Create a map of folders to export the images to
        """
        exportmap = []

        for begin, end, title in eventscuts:
            if title is None: continue

            for i in range(begin, end):

                # fill the map with empty values
                if len(exportmap)<=i:
                    while len(exportmap)<=i:
                        exportmap.append(None)

                if exportmap[i] is None: exportmap[i]=[]

                exportmap[i].append(title)


        for i in range(begin_frame, end_frame):
            # fill the map with empty values
            if len(exportmap)<=i:
                while len(exportmap)<=i:
                    exportmap.append(None)

            if exportmap[i] is None: exportmap[i]=[]

            if len(exportmap[i])==0:
                exportmap[i].append('untagged')
            
        return exportmap



    def __apply_event(self):

        if self._apply.checked:

            if self._usecut.value and self._imagesize.value>0:
                x, xx = self._cutx.value
                y, yy = self._cuty.value
                if int(yy)==int(y) or int(xx)==int(x):
                    self.message("The second cut value has to be bigger than the first", "Error", "error")
                    self._apply.checked=False
                    return

            self._toolbox.enabled   = False
            self._exportdir.enabled = False
            self._progress.value    = 0
            self._apply.label       = 'Cancel'

            # setup the progress bar
            total_2_analyse  = 0
            for video, (begin, end), datasets in self.datasets_dialog.selected_data:
                total_2_analyse += end-begin

            self._progress.min = 0
            self._progress.max = total_2_analyse
            self._progress.show()


            ######################################################################
            # create a directory to export the images if the option was selected
            EXPORT_DIRECTORY = self._exportdir.value
            if len(EXPORT_DIRECTORY)==0: EXPORT_DIRECTORY = 'contour-images'
            if not os.path.exists(EXPORT_DIRECTORY): os.makedirs(EXPORT_DIRECTORY)
            ######################################################################

         
            ############ CONFIGURE IMAGE CUT PARAMETERS ##########################
            params = {}
            params['mask']          = self._usemaskimg.value
            params['ellipse_mask']  = self._usemaskellipse.value
            params['rect_mask']     = self._usemaskrect.value
            params['margin']        = self._margin.value
            params['stretch']       = self._usestretch.value

            if self._usemaskdilate.value:
                params['mask']  = int(self._maskdilatesize.value)
            if self._usemaskcircular.value:
                params['circular_mask'] = int(self._maskcircularsize.value)
            if self._usefixedangle.value:
                params['angle'] = math.radians(self._fixedangle.value)
            if self._userotup.value:
                params['angle'] = 'up'
            if self._userotdown.value:
                params['angle'] = 'down'
            if self._imagesize.value>0:
                params['size']  = (self._imagesize.value, self._imagesize.value)
            ######################################################################

            ######################################################################            
            # check if should use the angle from other datasets
            if self._usedatasetangle.value:
                objects_angles = {}
                for _, _, datasets in self.datasets_dialog.selected_data:
                    for dataset in datasets:
                        for _, _, d in self._datasetanglepanel.value.selected_data:
                            objects_angles[dataset.object2d] = d[0]
            ######################################################################

            ######################################################################            
            # check if should use position from other datasets
            if self._useposdataset.value:
                objects_pos = {}
                for _, _, datasets in self.datasets_dialog.selected_data:
                    for dataset in datasets:
                        for _, _, d in self._datasetpospanel.value.selected_data:
                            objects_pos[dataset.object2d] = d[0]
            ######################################################################

                


            for video, (begin, end), datasets in self.datasets_dialog.selected_data:
                if not self._apply.checked: break

                if len(datasets)==0: continue
                begin, end  = int(begin), int(end)
                capture     = cv2.VideoCapture(video.filepath)
                capture.set(cv2.CAP_PROP_POS_FRAMES, begin); 
                
                eventscuts = self.__get_events_cuts(begin, end)
                exportmap  = self.__get_export_map(begin, end, eventscuts) 

                ######################################################################
                # create the directories to export the images per video and events
                videofolder = os.path.join(EXPORT_DIRECTORY, video.name)
                if not os.path.exists(videofolder): os.makedirs(videofolder)

                for dataset in datasets:
                    objectfolder = os.path.join(videofolder, dataset.object2d.name)
                    if not os.path.exists(objectfolder): os.makedirs(objectfolder)

                    datasetfolder = os.path.join(objectfolder, dataset.name)
                    if not os.path.exists(datasetfolder): os.makedirs(datasetfolder)
                ######################################################################

                for i in range(begin,end):
                    if not self._apply.checked: break

                    res, frame = capture.read()
                    #exit in the case the frame was not read.
                    if not res:
                        self._apply.label       = 'Apply'
                        self._toolbox.enabled   = True
                        self._exportdir.enabled = True
                        self._apply.checked     = False
                        self._progress.hide()       
                        return False, None

                    for foldername in exportmap[i]:
                        if not self._apply.checked: break
                       
                        for dataset in datasets:

                            parameters = dict(params)
                            parameters['frame'] = frame.copy()

                            # in the case we are using another dataset angle to rotate the image
                            if self._usedatasetangle.value:
                                dtangle = objects_angles.get(dataset.object2d, None)
                                if dtangle is not None:
                                    parameters['angle'] = dtangle.get_angle(i)
                                else:
                                    continue

                            if self._useposdataset.value:
                                dpos = objects_pos.get(dataset.object2d, None)
                                if dpos is not None:
                                    parameters['image_center'] = dpos.get_position(i)
                                else:
                                    continue

                            ok, img = dataset.get_image(i, **parameters)
                            if ok:
                                folder  = os.path.join(videofolder, dataset.object2d.name, dataset.name, foldername)
                                imgpath = os.path.join(folder, '{0}.png'.format(i) )
                                if not os.path.exists(folder): os.makedirs(folder)

                                if self._usecut.value and self._imagesize.value>0:
                                    x, xx = self._cutx.value
                                    y, yy = self._cuty.value
                                    img = img[int(y):int(yy), int(x):int(xx)]

                                cv2.imwrite(imgpath, img)

                    self._progress.value += 1
                
                

            self._apply.label       = 'Apply'
            self._toolbox.enabled   = True
            self._exportdir.enabled = True
            self._apply.checked     = False
            self._progress.hide()





    


if __name__ == '__main__': 
    pyforms.startApp(ContoursImagesWindow)
