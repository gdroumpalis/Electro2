class RendererParameters:
    def __init__(self, writetofile=False, rendering=False, renderingwindowwitdh=600, renderingwindowsheight=600,
                 filepath=str("")):
        self.writetofile = writetofile
        self.rendering = rendering
        self.renderingwindowheigh = renderingwindowsheight
        self.renderingwindowwidth = renderingwindowwitdh
        self.filepath = filepath
