#!/bin/bash
SOURCE=$1
WORK=`mktemp -d`
# remove path & extension
NAME=${SOURCE%.*}
NAME=${NAME##*/}
TYPE=`file -b $SOURCE | awk '{ print $1 }'`
DIR=`dirname $SOURCE`
LOG=ocr.log

pdfToTiff(){
 # conversion TIFF
  gs -q -sDEVICE=tiffg4 -dBATCH -dNOPAUSE -r500 -sOutputFile="$WORK/$NAME.tiff" "$SOURCE"
}

doOcr(){
  tesseract -l fra "$WORK/$NAME.tiff" "$WORK/$NAME" pdf 1>/dev/null
}

# $1 code de sortie
clean_exit(){
  rm -r $WORK
  exit $1
}

main(){
  if [ "PDF" == $TYPE ]
  then 
    pdfToTiff 2> >( sed "s/^/$(date '+[%F %T]') /">>$LOG )
  elif [ "TIFF" == $TYPE ]
  then
    mv "$SOURCE" "$WORK/." 2> >( sed "s/^/$(date '+[%F %T]') /">>$LOG )
  else 
    echo "$SOURCE"
    clean_exit 0
  fi
  if [ -f "$WORK/$NAME.tiff" ]
  then
    doOcr 2> >( sed "s/^/$(date '+[%F %T]') /">>$LOG) \
    	&& cp "$WORK/$NAME.pdf" "$DIR" 2> >( sed "s/^/$(date '+[%F %T]') /">>$LOG )
  fi
  if [ -f "$DIR/$NAME.pdf" ]
  then 
    echo "$DIR/$NAME.pdf"
    clean_exit 0
  else
    clean_exit 1
  fi
}

main

