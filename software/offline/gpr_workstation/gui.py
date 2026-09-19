import argparse,json,tkinter as tk
from tkinter import ttk,filedialog,messagebox
from pathlib import Path
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from .config import load_config
from .io import load_capture
from .pipeline import GPRPipeline
from .export import export_result
from .report import write_html_report
from .visualization import plot_ascan,plot_bscan,plot_spectrum,plot_3d_surface
class Workstation(tk.Tk):
 def __init__(self,input_path=None,config_path=None,metadata_path=None):
  super().__init__();self.title('RFSoC GPR Workstation');self.geometry('1500x920');self.input_path=input_path;self.config_path=config_path;self.metadata_path=metadata_path;self.cfg=load_config(config_path);self.cap=self.result=None;self._ui();self.after(150,self.process) if input_path else None
 def _ui(self):
  bar=ttk.Frame(self);bar.pack(fill='x');[(ttk.Button(bar,text=t,command=c).pack(side='left')) for t,c in [('Open capture',self.open_capture),('Load config',self.open_config),('Process',self.process),('Export',self.export)]];self.status=tk.StringVar(value='Ready');ttk.Label(bar,textvariable=self.status).pack(side='right')
  self.nb=ttk.Notebook(self);self.nb.pack(fill='both',expand=True);self.ax={};self.cv={}
  for title,key,three in [('A-scan','a',False),('B-scan','b',False),('Migration 2D','m',False),('Spectrum','s',False),('3D','d',True)]:
   fr=ttk.Frame(self.nb);self.nb.add(fr,text=title);fig=Figure(figsize=(9,6));ax=fig.add_subplot(111,projection='3d' if three else None);cv=FigureCanvasTkAgg(fig,fr);cv.get_tk_widget().pack(fill='both',expand=True);self.ax[key]=ax;self.cv[key]=cv
  fr=ttk.Frame(self.nb);self.nb.add(fr,text='Detections');self.tree=ttk.Treeview(fr,columns=('id','x','z','class','material','confidence'),show='headings');[self.tree.heading(c,text=c) for c in self.tree['columns']];self.tree.pack(fill='both',expand=True)
  fr=ttk.Frame(self.nb);self.nb.add(fr,text='Config');self.cfgtext=tk.Text(fr,font=('Consolas',9));self.cfgtext.pack(fill='both',expand=True);self.cfgtext.insert('1.0',json.dumps(self.cfg,indent=2))
  fr=ttk.Frame(self.nb);self.nb.add(fr,text='Diagnostics');self.diag=tk.Text(fr,font=('Consolas',10));self.diag.pack(fill='both',expand=True)
 def open_capture(self):
  p=filedialog.askopenfilename(filetypes=[('GPR','*.npz *.bin *.mat *.h5 *.hdf5')]);self.input_path=p or self.input_path
 def open_config(self):
  p=filedialog.askopenfilename(filetypes=[('Config','*.yaml *.yml *.json')]);
  if p:self.config_path=p;self.cfg=load_config(p);self.cfgtext.delete('1.0','end');self.cfgtext.insert('1.0',json.dumps(self.cfg,indent=2))
 def process(self):
  if not self.input_path:return
  try:self.cfg=json.loads(self.cfgtext.get('1.0','end'));self.cap=load_capture(self.input_path,self.metadata_path);self.result=GPRPipeline(self.cfg).run(self.cap);self.refresh();self.status.set('Complete')
  except Exception as e:messagebox.showerror('GPR',str(e))
 def refresh(self):
  r=self.result;c=self.cap;v=self.cfg['visualization'];mid=c.iq.shape[-1]//2;plot_ascan(self.ax['a'],r.range_m,r.background_removed[:,mid]);plot_bscan(self.ax['b'],c.x_m,r.range_m,r.background_removed,'B-scan',v['dynamic_range_db'],v['colormap']);plot_bscan(self.ax['m'],r.x_m,r.z_m,r.migrated,'Migrated 2-D',v['dynamic_range_db'],v['colormap'],r.detections);plot_spectrum(self.ax['s'],c.frequencies_hz,r.calibrated_iq[:,mid]);plot_3d_surface(self.ax['d'],r.x_m,r.z_m,r.migrated,v['dynamic_range_db']);[q.draw() for q in self.cv.values()]
  [self.tree.delete(i) for i in self.tree.get_children()];[self.tree.insert('', 'end',values=(d.id,'%.3f'%d.x_m,'%.3f'%d.depth_m,d.classification,d.material_hint,'%.2f'%d.confidence)) for d in r.detections];self.diag.delete('1.0','end');self.diag.insert('1.0',json.dumps(r.diagnostics,indent=2))
 def export(self):
  if self.result is None:return
  d=filedialog.askdirectory();
  if d:out=export_result(self.result,self.cfg,d);write_html_report(self.result,self.cfg,Path(out)/'report.html')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input');ap.add_argument('--config');ap.add_argument('--metadata');a=ap.parse_args();Workstation(a.input,a.config,a.metadata).mainloop()
if __name__=='__main__':main()
