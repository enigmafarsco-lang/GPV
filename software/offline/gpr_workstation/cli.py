import argparse,json
from .config import load_config
from .io import load_capture
from .pipeline import GPRPipeline
from .export import export_result
from .report import write_html_report
from .classification import train_from_csv
def main(argv=None):
 ap=argparse.ArgumentParser();s=ap.add_subparsers(dest='cmd',required=True);p=s.add_parser('process');p.add_argument('input');p.add_argument('--metadata');p.add_argument('--config',required=True);p.add_argument('--out',required=True);t=s.add_parser('train-classifier');t.add_argument('csv');t.add_argument('--out-model',required=True);t.add_argument('--label-column',default='label');a=ap.parse_args(argv)
 if a.cmd=='train-classifier':train_from_csv(a.csv,a.out_model,a.label_column);print(a.out_model);return
 cfg=load_config(a.config);cap=load_capture(a.input,a.metadata);r=GPRPipeline(cfg).run(cap);out=export_result(r,cfg,a.out,cap.frequencies_hz,cap.x_m);write_html_report(r,cfg,out/'report.html');print(json.dumps(r.diagnostics,indent=2));print(out)
if __name__=='__main__':main()
