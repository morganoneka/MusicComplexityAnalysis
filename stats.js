// https://snippets.bentasker.co.uk/page-1907020841-Calculating-Mean,-Median,-Mode,-Range-and-Percentiles-with-Javascript-Javascript.html

/** Calculate the mean value of an array of values
 *
 * @arg array
 * @return mixed
 */
function calcAverage(arr){
    var a = arr.slice();
    if (a.length){
        sum = sumArr(a);
        avg = sum / a.length;
        return avg;
    }
    return false;
}

/** Extract the maximum in an array of values
*
* @arg arr - array
* @return float
*/
function calcMax(arr){
    return Math.max(...arr);
}

/** Calculate the Median of an array of values
 *
 */
function calcMedian(arr){
        var a = arr.slice();
        hf = Math.floor(a.length/2);
        arr = sortArr(a);
        if (a.length % 2){
            return a[hf];
        }else{
            return (parseFloat(a[hf-1]) + parseFloat(a[hf])) / 2.0;
        }

}

/** Extract the maximum in an array of values
*
* @arg arr - array
* @return float
*/
function calcMin(arr){
    return Math.min(...arr);
}

/** Calculate the Modal value
*
* @arg arr - array
* @return float
*/
function calcMode(arr){
    var ary = arr.slice();
    t = ary.sort(function(a,b){
        ary.filter(function(val){
            val===a
        }).length - ary.filter(function(val){
            val===b
        }).length});
    return t.pop();
}

/** Calculate the 'q' quartile of an array of values
*
* @arg arr - array of values
* @arg q - percentile to calculate (e.g. 95)
*/
function calcQuartile(arr,q){
    var a = arr.slice();
    // Turn q into a decimal (e.g. 95 becomes 0.95)
    q = q/100;

    // Sort the array into ascending order
    data = sortArr(a);

    // Work out the position in the array of the percentile point
    var p = ((data.length) - 1) * q;
    var b = Math.floor(p);

    // Work out what we rounded off (if anything)
    var remainder = p - b;

    // See whether that data exists directly
    if (data[b+1]!==undefined){
        return parseFloat(data[b]) + remainder * (parseFloat(data[b+1]) - parseFloat(data[b]));
    }else{
        return parseFloat(data[b]);
    }
}

/** Calculate the range for a set of values
*
* @arg arr - array
* @return float
*/
function calcRange(arr){
    mx = calcMax(arr);
    mn = calcMin(arr);
    return mx-mn;
}

/** Sum all values in an array
 *
 */
function sumArr(arr){
    var a = arr.slice();
    return a.reduce(function(a, b) { return parseFloat(a) + parseFloat(b); });
}

/** Sort values into ascending order
*
*/
function sortArr(arr){
    var ary = arr.slice();
    ary.sort(function(a,b){ return parseFloat(a) - parseFloat(b);});
    return ary;
}
