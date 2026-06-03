// maximo comun divisor
int maximo_comun_divisor(int a, int b) {
    while (b != 0) {
        int temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

// concatenar cadenas
void concatenar_cadenas(char dest[], char src[]) {
    int i = 0;
    int j = 0;
    while (dest[i] != '\0') {
        i++;
    }
    while (src[j] != '\0') {
        dest[i] = src[j];
        i++;
    }
    dest[i] = '\0';
}

