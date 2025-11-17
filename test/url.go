package main

import (
	"fmt"
	"io"
	"net/http"
)

func main() {
	// Make a GET request
	resp, err := http.Get("https://snehasishroy-125.github.io/")
	if err != nil {
		fmt.Println("Error making request:", err)
		return
	}
	defer resp.Body.Close()

	// Read the response body
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("Error reading response:", err)
		return
	}

	// Print the response
	fmt.Println("Status:", resp.Status)
	fmt.Println("Body:", string(body))
}
