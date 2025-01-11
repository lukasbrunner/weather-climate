#!/bin/bash
# Calculate the mean seasonal cycle of a variable in a netCDF file

startyear=1940
endyear=2024
window=1  # fixed to 1 day

# Parse optional flags
while [[ "$#" -gt 0 ]]; do
    case $1 in
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
    echo "Usage: $0 infile.nc outpath [-s|--startyear STARTYEAR] [-e|--endyear ENDYEAR] [-v|--varn VARNAME]"
    exit 1
fi

infile="$1"
outpath="$2"
shift 2

# echo input
echo "Input file: $infile"
echo "Output path: $outpath"
echo "Start year: $startyear"
echo "End year: $endyear"

mkdir -p $outpath
outfile=$outpath/$(basename $infile .nc)

if [ ! -f ${outfile}_b${startyear}-${endyear}_365day.nc ]; then
    cdo setcalendar,365_day -delete,month=2,day=29 -selyear,$startyear/$endyear $infile ${outfile}_b${startyear}-${endyear}_365day.nc 
fi 

if [ ! -f ${outfile}_b${startyear}-${endyear}_w${window}_ydrunmean.nc ]; then
    cdo setattribute,window=${window},startyear=${startyear},endyear=${endyear} -ydaymean ${outfile}_b${startyear}-${endyear}_365day.nc ${outfile}_b${startyear}-${endyear}_w${window}_ydrunmean.nc
fi

if [ ! -f ${outfile}_b${startyear}-${endyear}_w${window}_ydrunmin.nc ]; then
    cdo ydaymin ${outfile}_b${startyear}-${endyear}_365day.nc ${outfile}_b${startyear}-${endyear}_w${window}_ydrunmin.nc
fi

if [ ! -f ${outfile}_b${startyear}-${endyear}_w1.nc ]; then
    cdo ydaymax ${outfile}_b${startyear}-${endyear}_365day.nc ${outfile}_b${startyear}-${endyear}_w${window}_ydrunmax.nc
fi

for percentile in $(seq 0 5 100); do
    if [ ! -f ${outfile}_b${startyear}-${endyear}_w${window}_p${percentile}.nc ]; then
        cdo setattribute,percentile=${percentile},window=${window},startyear=${startyear},endyear=${endyear} -ydaypctl,${percentile} ${outfile}_b${startyear}-${endyear}_365day.nc ${outfile}_b${startyear}-${endyear}_w${window}_ydrunmin.nc ${outfile}_b${startyear}-${endyear}_w${window}_ydrunmax.nc ${outfile}_b${startyear}-${endyear}_w${window}_p${percentile}.nc
    fi
done

if [ ! -f ${outfile}_b${startyear}-${endyear}_w${window}_std.nc ]; then
    cdo setattribute,percentile=${percentile},window=${window},startyear=${startyear},endyear=${endyear} -ydaystd ${outfile}_b${startyear}-${endyear}_365day.nc ${outfile}_b${startyear}-${endyear}_w${window}_std.nc
fi

rm ${outfile}_b${startyear}-${endyear}_365day.nc