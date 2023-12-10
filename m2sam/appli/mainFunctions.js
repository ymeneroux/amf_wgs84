// ----------------------------------------------------------
// Fichier contenant les fonctions principales du script
// ----------------------------------------------------------

// Variables globales
var tirage;
var nbkc;
var std;

// Accessibilité de save
var save_button = false;

// Answer table
var ANSWER_SHEET;

// Test mode
var mode;

var solution;

// ----------------------------------------------------------
// Fonctions d'affichage des champs d'observation
// Sortie : (void) remplissage de la balise "frm"
// ----------------------------------------------------------
function firstButton() {

    var x = document.getElementById("frm1000");
    var nb = x.elements[0].value;
	
	// Test nombre de questions
	if ((nb < 4)){
	
		// Message d'alerte 
		var alerte = '<div style="padding:5px; background-color:#ffaca3; border:2px solid #ff3924;';
		alerte += ' -moz-border-radius:9px; -khtml-border-radius:9px; -webkit-border-radius:9px; border-radius:9px;">';
		alerte += '<strong>Warning</strong> : ';
		alerte += +nb+' is not a valid choice. ';		
		alerte += 'The number of observations must be between 4 and 32. ';
		alerte += '</div>';
		
		document.getElementById("frm").innerHTML = alerte;
		
		return;
	
	}

	
	var ex_values = [
		["23636576.918",  "11916169.869",   "994662.691", "22845684.646"],
		[ "3630242.128",  "18111209.308", "19104527.037", "22787687.911"],
		["10663317.260",  "17081708.507", "17104548.858", "21723239.938"], 
		["13574544.694", "-17760136.706", "14629962.453", "22338260.138"],  
		["14943197.874",   "5402264.144", "21026251.997", "19993737.051"],  
		["23424863.869",  "-2092559.092", "12379581.734", "20623869.507"],
		[ "7868832.124", "-13079961.941", "21578356.311", "21541573.644"]];
		
		
		
		/*
	
	ex_values = [[29502324.0392,  39334549.8768, -19169751.5468, 33125228.7184],
				[1112663.055822,  -272063.414305, 31283557.092163, 56446439.0579],
				[-13966381.7548,  25918168.9292, -51839545.3084, 53718249.8562],
				[-88432222.58661,  47285650.36152,  -4006736.28106, 120990363.962],
				[-11120173.0951,  93312939.6127,  26442355.1447, 104426650.556]];
	*/
		
	var formulaire = '<p><i><b>Help</b>: on each row s, input: <br/>&nbsp&nbsp- <b>Xs</b>, <b>Ys</b>, <b>Zs</b> : coordinates (in m) of satellite s at measurement time <br/>&nbsp&nbsp- <b>Ds</b> : pseudo-distance (in m) to satellite s at measurement time</i></p><div></br>';
	for (i=0; i<nb; i++){
		formulaire +=    'Xs: <input type="text" name="field_i" id="field_'+i+'x" value="" required>';
		formulaire += '&nbsp m &nbsp &nbsp &nbsp   Ys: <input type="text" name="field_i" id="field_'+i+'y" value="" required> ';
		formulaire += '&nbsp m &nbsp &nbsp &nbsp   Zs: <input type="text" name="field_i" id="field_'+i+'z" value="" required> ';
		formulaire += '&nbsp m &nbsp &nbsp &nbsp   Ds: <input type="text" name="field_i" id="field_'+i+'d" value="" required>&nbsp m</br></br>';
	}
	
	
2
	
	
	formulaire += '<div class=\"buttons\"><a href="#" class="button start" onclick="secondButton()">SOLVE</a></div>';
	
	formulaire += '</div>';
	
	document.getElementById("frm").innerHTML = formulaire;
	
	return
}


// ----------------------------------------------------------
// Fonctions d'impression d'une matrice
// ----------------------------------------------------------
function printMatrix(matrix){
	var solution = '<table>';
	for (i=1; i<=matrix.rows(); i++){
		solution += '<tr>';
		for (j=1; j<=matrix.cols(); j++){
			solution += '<td align="right">';
			solution += '&nbsp &nbsp' + matrix.e(i,j) + '&nbsp &nbsp';
			solution += '</td>';
		}	
		solution += '</tr>';
	}
	solution += '</table>';
	return solution;
}


// ----------------------------------------------------------
// Fonctions de calcul de la solution
// Sortie : (void) remplissage de la balise "sol"
// ----------------------------------------------------------
function secondButton() {
	
	// ------------------------------------------------------
	// Collecting data from forms
	// ------------------------------------------------------
	
	solution  = "</br></br></br>";
	solution += "---------------------------------------------</br>";
	solution += "DETAILS </br>";
	solution += "---------------------------------------------</br></br>";
	
	solution += '</br>Observations : </br></br>';

	var nb = parseInt(document.getElementById("spinner").value);
	
	var elements = []; 
	for (i=0; i<nb; i++){
		var row = []; 
		row.push(parseFloat(document.getElementById("field_"+i+"x").value)); 
		row.push(parseFloat(document.getElementById("field_"+i+"y").value));
		row.push(parseFloat(document.getElementById("field_"+i+"z").value));
		row.push(parseFloat(document.getElementById("field_"+i+"d").value));
		elements.push(row);
	}	
	
	var DATA = Matrix.create(elements);
	
	solution += printMatrix(DATA);
	
	
	// ------------------------------------------------------
	// Solving problem
	// ------------------------------------------------------
	var X = Matrix.create([[0],[0],[0],[0]]);
	
	
	for (iter=0; iter<100; iter++){
		
		solution += "</br></br>---------------------------------------------</br>";
		solution += "Iteration "+(iter+1)+"</br>";
		solution += "---------------------------------------------</br></br>";
		
		var x = X.e(1,1); var y = X.e(2,1); var z = X.e(3,1); var cdt = X.e(4,1);
		
		var elem2 = []; 
		var elem3 = [];
		
		
		for (i=0; i<nb; i++){
			var row2 = []; 
			var row3 = []
			var Xs = DATA.e(i+1, 1); var Ys = DATA.e(i+1, 2); var Zs = DATA.e(i+1, 3); 
			var dx = x-Xs; var dy = y-Ys; var dz = z-Zs;
			var Rs = Math.sqrt(dx*dx + dy*dy + dz*dz);
			
			row2.push(dx/Rs); 
			row2.push(dy/Rs);
			row2.push(dz/Rs);
			row2.push(1.0);
			elem2.push(row2);
			
			row3.push(DATA.e(i+1,4) - (Rs + cdt));
			elem3.push(row3);
			
		}	
		
		var A = Matrix.create(elem2);
		var B = Matrix.create(elem3);
		
		solution += "X = </br> " + printMatrix(X) + "</br>";
		solution += "A = </br> " + printMatrix(A) + "</br>";
		solution += "B = </br> " + printMatrix(B) + "</br>";
		
		
		var N = ((A.transpose().multiply(A)).inv());
		var dX = N.multiply(A.transpose().multiply(B));
		var rmse = (Math.sqrt(B.transpose().multiply(B).e(1,1)/nb))
		var norm_dx = (Math.sqrt(dX.transpose().multiply(dX).e(1,1)/nb))
		
		solution += "dX = </br> " + printMatrix(dX)+ "</br>";
		solution += "RMSE = " + rmse.toFixed(3) + " m &nbsp &nbsp &nbsp";
		solution += "||dX|| = " + norm_dx.toFixed(3) + " m</br>";
		
		X = X.add(dX);
		
		if (norm_dx < 1e-6){
			break
		}
	
	}
	
	
	solution += "</br> </br> </br></br>";
	
	solution += "---------------------------------------------</br>";
	solution += "SOLUTION </br>";
	solution += "---------------------------------------------</br></br>";
	solution += "<b>X = </br> " + printMatrix(X)+"</b>";
	

	//document.getElementById("details").innerHTML = solution;
	
	
	
	var max_res = B.e(1,1);
	var id_max_res = 1;
	for (i=2; i<=B.rows(); i++){
		if (Math.abs(B.e(i,1)) > max_res){
			max_res = Math.abs(B.e(i,1));
			id_max_res = i;
		}
	}
	
	 
	var sx = Math.sqrt(N.e(1,1));
	var sy = Math.sqrt(N.e(2,2));
	var sz = Math.sqrt(N.e(3,3));
	var st = Math.sqrt(N.e(4,4));
	
	var pdop = Math.sqrt(sx*sx + sy*sy + sz*sz);
	var tdop = st;
	var gdop = Math.sqrt(pdop*pdop + tdop*tdop);
	
	
	var solution_globale  = "</br></br><b> Solution :</br></br>";
	solution_globale += "X = " + (X.e(1,1)).toFixed(3) + " m  &nbsp &nbsp &nbsp";
	solution_globale += "Y = " + (X.e(2,1)).toFixed(3) + " m  &nbsp &nbsp &nbsp";
	solution_globale += "Z = " + (X.e(3,1)).toFixed(3) + " m  &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp";
	solution_globale += "dt = " + (X.e(4,1)).toFixed(3) + " m;"
	solution_globale += "</b></br></br> RMSE = "+ rmse.toFixed(2) + " m &nbsp &nbsp &nbsp";
	solution_globale += "MAX RESIDUAL = "+ max_res.toFixed(2) + " m &nbsp";
	solution_globale += "FOR OBS #"+ id_max_res + "&nbsp &nbsp &nbsp";
	solution_globale += "(convergence reached after " + iter + " iterations) </br></br>";
	solution_globale += "STD:&nbsp SX = "+ (rmse*sx).toFixed(0) + " m </br>";
	solution_globale += "&nbsp &nbsp &nbsp SY = "+ (rmse*sy).toFixed(0) + " m </br>";
	solution_globale += "&nbsp &nbsp &nbsp SY = "+ (rmse*sz).toFixed(0) + " m </br>";
	solution_globale += "&nbsp &nbsp &nbsp ST = "+ (rmse*st).toFixed(0) + " m</br></br>";
	solution_globale += "PDOP = " + pdop.toFixed(2) + "&nbsp &nbsp &nbsp";
	solution_globale += "TDOP = " + tdop.toFixed(2) + "&nbsp &nbsp &nbsp";
	solution_globale += "GDOP = " + gdop.toFixed(2) + "</br>";
	solution_globale += "</br></br>";
	
	
	solution_globale += "RESIDUALS: </br>";
	for (i=1; i<=nb; i++){
		solution_globale += "OBS #"+i+" ";
		for (j=0; j<100; j++){
			if (Math.abs(B.e(i,1))/max_res > j/100){
				solution_globale += "x";
			}else{
				solution_globale += "-";
			}
			
		}
		solution_globale += "|</br>";
	}
	
	solution_globale += "</br></br></br>";


	solution_globale += '<div class=\"buttons\"><a href="#" class="button start" onclick="thirdButton()">DETAILS</a></div>';

	
	document.getElementById("sol").innerHTML = solution_globale;

	return
	
}
	
	
// ----------------------------------------------------------
// Fonctions d'affichage des détails
// Sortie : (void) remplissage de la balise "details"
// ----------------------------------------------------------
function thirdButton() {
	document.getElementById("details").innerHTML = solution;
	return;
}
