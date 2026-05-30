/*
	Filename: fir_test.h
		FIR lab wirtten for WES/CSE237C class at UCSD.
		Testbench file
		Calls fir() function from fir.cpp
		Compares the output from fir() with out.gold.dat
*/

#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include "fir.h"

static FILE* open_data_file(const char* name, const char* mode) {
  FILE* fp = fopen(name, mode);
  if (fp != NULL) {
    return fp;
  }

  char fallback_path[512];
  snprintf(fallback_path, sizeof(fallback_path), "../../../../%s", name);
  return fopen(fallback_path, mode);
}

int main () {
  const int    SAMPLES=600;
  FILE         *fp, *fin;

  data_t signal, output;
  int i;
  signal = 0;
  

  fin=open_data_file("input.dat","r");
  fp=fopen("out.dat","w");

  if (fin == NULL || fp == NULL) {
    perror("failed to open testbench data file");
    if (fp != NULL) fclose(fp);
    if (fin != NULL) fclose(fin);
    return 1;
  }

  for (i=0;i<SAMPLES;i++) {
	fscanf(fin,"%d",&signal);
	//Call the HLS block
    fir(&output,signal);
    // Save the results.
    fprintf(fp,"%d\n",output);
    printf("%i %d %d\n",i,signal,output);
  }

  fclose(fp);
  fclose(fin);

  //Comparing results with the golden output.
  printf ("Comparing against output data \n");
    if (system("diff -w out.dat out.gold.dat")) {
  	fprintf(stdout, "*******************************************\n");
  	fprintf(stdout, "FAIL: Output DOES NOT match the golden output\n");
  	fprintf(stdout, "*******************************************\n");
       return 1;
    } else {
  	fprintf(stdout, "*******************************************\n");
  	fprintf(stdout, "PASS: The output matches the golden output!\n");
  	fprintf(stdout, "*******************************************\n");
       return 0;
    }

}
