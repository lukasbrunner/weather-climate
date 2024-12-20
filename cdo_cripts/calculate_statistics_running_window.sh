#!/bin/bash
# Calculate the mean seasonal cycle of a variable in a netCDF file

window=31
startyear=1961
endyear=1990

# Parse optional flags
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -w|--window) window="$2"; shift ;;
        -s|--startyear) startyear="$2"; shift ;;
        -e|--endyear) endyear="$2"; shift ;;
        --) shift; break ;;
        -*) echo "Unknown option: $1" >&2; exit 1 ;;
        *) break ;;
    esac
    shift
done

# Check if mandatory input file and output path are provided
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 infile.nc outpath [-w|--window WINDOW] [-s|--startyear STARTYEAR] [-e|--endyear ENDYEAR] [-v|--varn VARNAME]"
    exit 1
fi

infile="$1"
outpath="$2"
shift 2

# echo input
echo "Input file: $infile"
echo "Output path: $outpath"
echo "Window: $window"
echo "Start year: $startyear"
echo "End year: $endyear"

mkdir -p $outpath
outfile=$outpath/$(basename $infile .nc)

if [ ! -f ${outfile}_b${startyear}-${endyear}_365day.nc ]; then
    cdo setcalendar,365_day -delete,month=2,day=29 -selyear,$startyear/$endyear $infile ${outfile}_b${startyear}-${endyear}_365day.nc 
fi 

if [ ! -f ${outfile}_b${startyear}-${endyear}_w${window}_ydrunmean.nc ]; then
    cdo setattribute,window=${window},startyear=${startyear},endyear=${endyear} -ydrunmean,$window,rm=c ${outfile}_b${startyear}-${endyear}_365day.nc ${outfile}_b${startyear}-${endyear}_w${window}_ydrunmean.nc
fi

if [ ! -f ${outfile}_b${startyear}-${endyear}__w${window}_anomalies.nc ]; then
    cdo sub ${outfile}_b${startyear}-${endyear}_365day.nc ${outfile}_b${startyear}-${endyear}_${window}_ydrunmean.nc ${outfile}_b${startyear}-${endyear}_w${window}_anomalies.nc
fi

if [ ! -f ${outfile}_b${startyear}-${endyear}_w${window}_ydrunmin.nc ]; then
    cdo ydrunmin,$window,rm=c ${outfile}_b${startyear}-${endyear}_w${window}_anomalies.nc ${outfile}_b${startyear}-${endyear}_w${window}_ydrunmin.nc
fi

if [ ! -f ${outfile}_b${startyear}-${endyear}_w${window}_ydrunmax.nc ]; then
    cdo ydrunmax,$window,rm=c ${outfile}_b${startyear}-${endyear}_w${window}_anomalies.nc ${outfile}_b${startyear}-${endyear}_w${window}_ydrunmax.nc
fi

for percentile in $(seq 0 5 100); do
    if [ ! -f ${outfile}_b${startyear}-${endyear}_w${window}_p${percentile}.nc ]; then
        cdo setattribute,percentile=${percentile},window=${window},startyear=${startyear},endyear=${endyear} -add -ydrunpctl,${percentile},$window,rm=c,pm=r8 ${outfile}_b${startyear}-${endyear}_w${window}_anomalies.nc ${outfile}_b${startyear}-${endyear}_w${window}_ydrunmin.nc ${outfile}_b${startyear}-${endyear}_w${window}_ydrunmax.nc ${outfile}_b${startyear}-${endyear}_w${window}_ydrunmean.nc ${outfile}_b${startyear}-${endyear}_w${window}_p${percentile}.nc
    fi
done

if [ ! -f ${outfile}_std_${window}_${startyear}-${endyear}.nc ]; then
    cdo setattribute,window=${window},startyear=${startyear},endyear=${endyear} -ydrunstd,$window,rm=c ${outfile}_b${startyear}-${endyear}_w${window}_anomalies.nc ${outfile}_b${startyear}-${endyear}_w${window}_std.nc
fi

rm ${outfile}_b${startyear}-${endyear}_365day.nc
